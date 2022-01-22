# lexiconBased_SA_NL
Code to perform lexicon-based sentiment analysis on a Dutch dataset

This folder contains code to perform lexicon-based sentiment analysis on Dutch data.
Requirements:
* Install CRF++ in your virtual env
* Make sure to a local copy of the Lets Preprocess (https://github.ugent.be/lt3/lets) folder to your Pythonpath
* See pipfile

## General  info
* Sentence boundaries in the input text should be indicated with the '[EOS]' token.
* Negation is taken into account (check the words in the negation list on top of the script)
* Gold standard sentiment labels should pertain to the following: 'very_negative', 'negative', 'positive', 'very_positive', 'neutral', 'objective'
* The system outputs a numeric sentiment score per sentence and maps this to pos/neg/neu to calculate the accuracy.
* SA accuracy is printed in the terminal; if you want to re-calculate it using the outfile, you'll need to map the scores to -1, 0.0 and 1, as is done by the script.
* **!! The script predicts sentiment scores at the sentence level; you decide how you aggregate for post-level predictions.**


The lexicons that are used are generic, so the code can be run on several types of text genres (social media, blogs, newspaper text, reviews,...).
There are four Dutch lexica used --> only entries with the following PoS-tags are considered: ADJ, WW, BW, N
	1. Duoman: 8,757 wordforms (Jijkoun, 2009)
	2. Pattern: 3,223 qualitative adjectives (Desmedt, 2012)
	3. NRC Hashtag lexicon: 13,683 wordforms (Mohammad, 2013) > automatically translated from English.
	4. In-house sentiment lexicon (constructed by Orphée De Clercq): 434 wordforms
All of them were manually revised by a job student (Annaïs Airapetian) in the summer of 2019.

The lexica are searched in a specific order; i.e. if a given word is not found in lexicon 1, it is searched for in lexicon 2, etc. If a word was found in lexicon 1, then no further lookup in lexicon 2, 3 and 4 is done. This order is experimentally determined by Cynthia Van Hee; the purpose of these experiments was finding out which lexicon is the most reliable for sentiment analysis in an order from best to last.

## Script input
* Path to the input file; a tab-separated file wih a gold-standard label and the text to be analyzed (1 instance = 1 line; make sure to replace newlines within a post with '[EOS]' to indicate sentence boundaries!)
* Path to the output folder

## Script output
	* A tab-separated file with the gold label, the predicted label and the original text. Format: 1 sentence per line, instances are separated by empty lines.
	* A .txt file with all the sentiment words that were matched against the sentiment lexica (for qualitative analysis purposes).


### Lexicon references

@inproceedings{Desmedt2012,
    title = {''Vreselijk mooi!'' (terribly beautiful): A Subjectivity Lexicon for {D}utch Adjectives.},
    author = {De Smedt, Tom  and Daelemans, Walter},
    booktitle = {Proceedings of the Eighth International Conference on Language Resources and Evaluation ({LREC}'12)},
    month = may,
    year = {2012},
    address = {Istanbul, Turkey},
    publisher = {ELRA},
    url = {http://www.lrec-conf.org/proceedings/lrec2012/pdf/312_Paper.pdf},
    pages = {3568--3572}
}


@inproceedings{Jijkoun2009,
    author = {Jijkoun, Valentin and Hofmann, Katja},
    title = {Generating a Non-English Subjectivity Lexicon: Relations That Matter},
    year = {2009},
    publisher = {ACL},
    address = {USA},
    booktitle = {Proceedings of the 12th Conference of the European Chapter of the Association for Computational Linguistics},
    pages = {398–405},
    numpages = {8},
    location = {Athens, Greece},
    series = {EACL'09}
}

@article{Mohammad2013,
	author = {Mohammad, Saif M. and Turney, Peter D.},
	journal = {Computational Intelligence},
	number = {3},
	pages = {436--465},
	title = {Crowdsourcing a Word-Emotion Association Lexicon},
	volume = {29},
	year = {2013}
}
