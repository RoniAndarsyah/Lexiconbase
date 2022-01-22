#!usr/bin/env python
# encoding: utf-8

"""
SentimentObjects.py

"""


class SentimentEntry:
    def __init__(self, Lemma, PoSTag, sentimentPolarityValue, dictionary):
        '''SentimentWord constructor'''
        self.Lemma = Lemma
        self.PoSTag = PoSTag
        self.SentimentPolarityValue = sentimentPolarityValue
        self.Dictionary = dictionary


class SentimentDictionary:
	def __init__(self, Name, Dictionary):
		self.Name = Name
		self.Dictionary = Dictionary


class WordObject:
	def __init__(self, Word, Lem, PoS):
		self.Word = Word
		self.Lem = Lem
		self.PoS = PoS
		self.IsNegated = False

class SentenceObject:
	def __init__(self, OriSentence, SentencePolarity, WordObjects):
		self.OriSentence = OriSentence
		self.SentencePolarity = SentencePolarity
		self.WordObjects = WordObjects