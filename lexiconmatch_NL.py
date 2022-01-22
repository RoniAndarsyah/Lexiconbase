#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2020 LT3, Ghent University, Belgium. All rights reserved.
Author: Cynthia Van Hee

Script for lexicon-based sentiment:
Matches sentiment lexicons (Duoman, Pattern, ABSA in-house lexicon, NRC) to company reviews and defines sentiment at the sentence level.
IMPORTANT:
    - Input format = 1 text per line. If the text contains multiple sentences, make sure these are separated using the `[EOS]' token, don't use pipes or other symbols.

Makes use of Lets Preprocess.

Note: for a version of this script that prints the sentiment dictionary matches in the terminal; see folder 'MP_SielDebouver'.
"""

import os
import sys

import xml.etree.cElementTree as ET
from SentimentObjects import SentimentEntry, SentimentDictionary, WordObject, SentenceObject
from lets.preprocessor import PreProcessor
import codecs

negatorlist = ["niet", "nee", "neen", "geen", "nooit", "zonder", "niemand", "nergens", "niets", "noch", "behalve"]

def get_dict_object(xmldoc):
    '''Reads lexicon (XML file), maps string labels to floats and add all entries to a dict.
    XMLdoc are lexicon XML files files of the format: <lexitem instances="1" lemma="" polarity="very_negative" pos="ADJ" wordform="achteloos"/>
    IMPORTANT: for words that occur in different lexica (with different sentiment labels): there is an order defined for the lexica based on their quality, so when the word has already been found in a lexicon, it will be ignored when found in a following lexicon.'''
    tree = ET.parse(xmldoc)
    root = tree.getroot()
    lexiconname = [el.attrib["domain"] for el in root.iter('Lexicon')]
    assert len(lexiconname) == 1
    lexitems = [el for el in root.iter('lexitem')]
    dictionary = {}
    postags = ['adj', 'n', 'ww', 'bw'] # Only consider content word entries! (otherwise the preposition 'voor' for instance, is also considered as a polword)
    for item in lexitems:
        lemma = item.attrib["lemma"]
        postag = item.attrib["pos"]
        wordform = item.attrib["wordform"]
        polarity = item.attrib["polarity"]
        if postag.lower() in postags:
            if polarity == "positive":
                value = 1.0
            elif polarity == "very_positive":
                value = 2.0
            elif polarity == "negative":
                value = -1.0
            elif polarity == "very_negative":
                value = -2.0
            elif polarity == "neutral":
                value = 0.0
            elif isinstance(float(polarity),float): # In the Pattern lexicon, polarity instances are floats.
                value = float(polarity)
            else:
                print("Unknown polarity value:{0}".format(polarity))
            if lemma: # Add lemmas to the dictionary if available
                entry = lemma
            else: # The Duoman and NRC lexicon don't provide lemmas
                entry = wordform
            if not entry.lower() in dictionary: 
                dictionary[entry.lower()] = SentimentEntry(lemma, [postag], [value], lexiconname)
            else: # Sometimes an entry occurs multple times with different PoS-tags or different sentiment values (e.g. "fout" in the NRC lexicon). Include all those PoS-tags and sentiment values as a list.
                dictionary[entry.lower()].PoSTag.append(postag)
                dictionary[entry.lower()].SentimentPolarityValue.append(value)
    for k, v in dictionary.items():
        if len(v.PoSTag) > 1 and len(list(set(v.PoSTag))) ==1: # If all the PoS-tags and sentiment values are the same (e.g. 'lui' in Duoman), only keep one entry
            if len(list(set(v.SentimentPolarityValue))) == 1:
                dictionary[k].PoSTag = [v.PoSTag[0]]
                dictionary[k].SentimentPolarityValue = [float(v.SentimentPolarityValue[0])]
            else:
                # If there is an entry with the same PoS-tag occurring multiple times but with different sentiment values (e.g. 'verdacht' in NRC), take the average of the values
                # print(k, v.Lemma, v.PoSTag, v.SentimentPolarityValue, v.Dictionary)
                pols = []
                for indx, pt in enumerate(v.PoSTag):
                    pols.append(v.SentimentPolarityValue[indx])
                dictionary[k].PoSTag = [v.PoSTag[0]]
                dictionary[k].SentimentPolarityValue = [float(sum(pols)/len(pols))]
                # print('new entry:', k, v.Lemma, v.PoSTag, v.SentimentPolarityValue, v.Dictionary)
    return SentimentDictionary(lexiconname[0], dictionary)


def get_sentiment_from_lexicon(lexicondictobjectlist, testfile, outdir):
    '''>>> MAIN SCRIPT <<<
    Matches lexicons to calculate sentiment at the sentence level.
    
    INPUT:
    - lexicondictobjectlist = list containing all lexicon dictionaries (in the order in which the lexicons should be matched, the first lexicon in the list will be the first to be matched! If no match is found for a word, it will be searched in the second lexicon, etc.)
    - testfile = tab-separated (gold label<TAB>text to be predicted), e.g. `negative<TAB>Toen ik mijn bestelling probeerde te plaatsen , liep de site meerdere keren vast'.
    - outdir = dir where the output files will be written to

    OUTPUT:
    - outfile with gold label, predicted label, and original text (at the sentence level)
    - outfile with, per sentence, a list of all words that were matched in the sentiment lexica
    - Printed in the terminal: sentiment analysis accuracy (i.e. predicted vs gold sentiment)'''
    correct = 0
    all_instances = 0
    predictionsdict = {}
    golddict = {}
    texts = codecs.open(testfile, 'r').readlines()
    lexiconname = '+'.join([x.Name for x in lexicondictobjectlist]) #Which lexicons are we predicting with?
    predictionsfilename = os.path.basename(testfile).replace('.txt', ('_predictions_' + lexiconname + '.txt'))
    predictionsf = codecs.open(os.path.join(outdir, predictionsfilename), 'w')
    predictionsf.write('GOLD\tPREDICTED\tTEXT\n')
    sentimentmatchesfilename = os.path.basename(testfile).replace('.txt', ('_sentimentMatches_' + lexiconname + '.txt'))
    sentimentmatchesf = codecs.open(os.path.join(outdir, sentimentmatchesfilename),'w')
    sentimentmatchesf.write('SENTIMENT WORD\tSENTIMENT VALUE\tPOS-TAG\tLEXICON\tTEXT\n')
    for text in texts:
        processed_sentences = prepro_instance(text)
        for sentenceObject in processed_sentences:
            all_instances += 1
            mapped_gold_label = map_gold_label(sentenceObject.SentencePolarity)
            #Check whether words are negated (important for polarity)
            for i, wordobject in enumerate(sentenceObject.WordObjects):
                if sentenceObject.WordObjects[i-1].Word.lower() in negatorlist:
                    # print('IS NEGATED:', sentenceObject.WordObjects[i].Word, sentenceObject.WordObjects[i].PoS)
                    # print('negator:', sentenceObject.WordObjects[i-1].Word)
                    sentenceObject.WordObjects[i].IsNegated = True
            lexiconmatches, all_polarities = match_lexicon(lexicondictobjectlist, sentenceObject.WordObjects)
            predictedlabel = float(sum(all_polarities))
            predictionsf.write('{0}\t{1}\t{2}\n'.format(mapped_gold_label, predictedlabel, sentenceObject.OriSentence.strip()))
            for lm in lexiconmatches:
                entry, polval, pos, lexiconname = lm
                sentimentmatchesf.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(entry, polval, pos, lexiconname, sentenceObject.OriSentence.strip()))
            #Check prediction with gold label to calculate ACC
            if mapped_gold_label == 1.0 and predictedlabel > 0.0:
                correct += 1
            elif mapped_gold_label == -1.0 and predictedlabel < 0.0:
                correct += 1
            elif mapped_gold_label == 0.0 and predictedlabel == 0.0:
                correct += 1
        predictionsf.write('\n') # Separate instances by an empty line
    print('>> Sentiment lexicon predictions written to file:\t{0}'.format(predictionsfilename))
    print('>> Sentiment lexicon matches written to file:\t{0}'.format(sentimentmatchesfilename))
    acc = round((correct/all_instances)*100,2)
    print('Prediction accuracy (sentence level):\t{0}% ({1}/{2})'.format(acc, correct, all_instances))
    predictionsf.close()
    sentimentmatchesf.close()


def prepro_instance(instance):
    '''Preprocesses the instance (i.e. a review, social media or blog post, etc.)
    Format: gold label<TAB>instance (can contain newlines and multiple sentences!).'''
    processed_instance = []
    if instance.strip():
        polaritylabel, text = instance.split('\t')
        preprocessor = PreProcessor(l='nl')
        sentences = text.split('[EOS]')
        for s in sentences:
            wordobjectlist = []
            prepro_s = preprocessor.process_lines([s.strip()])
            for line in prepro_s:
                fields = line.split('\t')
                if fields:
                    tok = fields[0]
                    lem = fields[1]
                    pos = fields[2].split('(')[0] #We only want the coarse-grained PoS-tag
                    wordobjectlist.append(WordObject(tok, lem, pos))
            processed_instance.append(SentenceObject(s, polaritylabel, wordobjectlist))
    return processed_instance


def map_gold_label(goldlabel):
    '''Maps the GS label to -1.0, 0.0 and 1.0'''
    if goldlabel.lower()in ['positive', 'very_positive']:
        label = 1.0
    elif goldlabel.lower() in ['negative', 'very_negative']:
        label = -1.0
    elif goldlabel.lower()in ['neutral', 'objective']:
        label = 0.0
    else:
        print('WARNING: gold-standard label not recognized:{0}'.format(goldlabel))
        label = goldlabel
    return label


def match_lexicon(lexicondictobjectlist, tokenized_string):
    '''Matches sentiment lexica to all words in the input text. In case words are preceded by a negation word, their polarity value is flipped.
    OUTPUT = all unique sentiment lexicon words found in the text and their polarity (including duplicate words)'''
    lexiconmatches = [] # Get all sentiment lexicon matches and their polarity
    all_polarities = [] # Also consider words that occur more than once in the string
    for wordObject in tokenized_string:
        if not wordObject.Word in negatorlist: #Assert word is not a negator
            found = False
            for dictionaryObject in lexicondictobjectlist:
                if not found:
                    lexicondict = dictionaryObject.Dictionary
                    entry = False
                    if wordObject.Lem in lexicondict:
                        entry = wordObject.Lem
                    elif wordObject.Word in lexicondict:
                        entry = wordObject.Word
                    if entry: # If the word form or the lemma can be matched against a lexicon, get the PoS-tag & sentiment label
                        if wordObject.PoS in lexicondict[entry].PoSTag: # Check whether the PoS-tags correspond
                            # Get the PoS index (because there can be multiple PoS-tags for an entry) and use that index to retrieve the relevant sentiment value
                            index = lexicondict[entry].PoSTag.index(wordObject.PoS)
                            polarityvalue = lexicondict[entry].SentimentPolarityValue[index]
                            if wordObject.IsNegated: # Flip the polarity value if the word is negated
                                polarityvalue = polarityvalue * -1
                            lexiconmatches.append((wordObject.Word, polarityvalue, wordObject.PoS, dictionaryObject.Name)) # Keep track of all matched sentiment words
                            all_polarities.append(polarityvalue)
                            found = True # If there is no match found in this dict, search in the following dict
                        else:
                            continue
                            print('Warning: word found, but PoS-tag does not correspond:', wordObject.Word, wordObject.PoS, lexicondict[wordObject.Word].PoSTag, 'Dictionary:', dictionaryObject.Name)
    return lexiconmatches, all_polarities



def main():
    print('Loading lexicons...')

    pollDictObject = get_dict_object('lexicons/fulllexicon_pol.xml')
    patternDictObject = get_dict_object('lexicons/pattern_lexicon_full.xml')
    NRCDictObject = get_dict_object('lexicons/NRC.xml')
    DuomanDict_object = get_dict_object('lexicons/Duoman.xml')

    print('Loading test file...')
    get_sentiment_from_lexicon([patternDictObject,pollDictObject,DuomanDict_object,NRCDictObject], './input/test.txt', './output/')



if __name__ == '__main__':
    main()
