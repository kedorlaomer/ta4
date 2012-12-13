#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import re

import nltk

from helpers import (
    suffixes, prefixes, isNominalTag, isVerbalTag, extremelyNormalize,
)


# A class for extracting features from sentences.
class Features(object):
    _stopwords = None
    _geneNames = None
    _genesDict = None

    def __init__(self, stopwords, geneNames):
        self._stopwords = set(stopwords)
        self._geneNames = set(geneNames)
        self._initGenesDict()

    def _initGenesDict(self):
        self._genesDict = {}
        for gene in self._geneNames:
            gene += "\n"
            curr_gene = ""
            firstFound = False
            for c in gene:
                if c != "\n":
                    curr_gene += c
                if not c.isalnum():
                    if firstFound:
                        classification = "I-protein"
                    else:
                        classification = "B-protein"
                        firstFound = True
                    self._genesDict[curr_gene] = classification
                    curr_gene = ""

    # Returns a list of dictionaries, one for each token in sentence (which should
    # be a list of strings). The keys are names of features, the values are bools
    def featuresForSentence(self, sentence):
        rv = dict()
        tagged = nltk.pos_tag(sentence)
        # Großbuchstabe nicht am Anfang
        p1 = re.compile(r'([\w]+|[\W]+)[A-Z]')
        # Sonderzeichen im Wort
        p2 = re.compile(r'([\w]*[a-zA-Z]+[\w]*[\W]+)|(([\w]*[\W]+[\w]*)+[a-zA-Z]+)')
        # Zahl im Wort
        p3 = re.compile(r'([\D]*[a-zA-Z]+[\D]*[\d]+)|(([\D]*[\d]+[\D]*)+[a-zA-Z]+)')

        for (i, (token, tag)) in enumerate(tagged):
            d = {}

            # suffixes
            for s in suffixes(token):
                d[s] = True

            # prefixes
            for p in prefixes(token):
                d[p] = True

            # its own POS tag
            d["nominal"] = isNominalTag(tag)
            d["verbal"] = isVerbalTag(tag)

            # predecessors's POS tags
            if i > 0:
                d["post-nominal"] = isNominalTag(tagged[i - 1][1])
                d["post-verbal"] = isVerbalTag(tagged[i - 1][1])

            # pre-predecessors's POS tags
            if i > 1:
                d["post-post-nominal"] = isNominalTag(tagged[i - 2][1])
                d["post-post-verbal"] = isVerbalTag(tagged[i - 2][1])

            # successors's POS tags
            if i < len(sentence) - 1:
                d["pre-nominal"] = isNominalTag(tagged[i + 1][1])
                d["pre-verbal"] = isVerbalTag(tagged[i + 1][1])

            # pre-predecessors's POS tags
            if i < len(sentence) - 2:
                d["pre-pre-nominal"] = isNominalTag(tagged[i + 2][1])
                d["pre-pre-verbal"] = isVerbalTag(tagged[i + 2][1])

            d["capital in word"] = p1.match(token) is not None
            d["special characters"] = p2.match(token) is not None
            d["contains digit"] = p3.match(token) is not None

            rv[i] = d

        return rv

    def featuresForWord(self, word):
        if not word:
            return {}

        rv = {}
        word_len = len(word)

        if word_len == 1:
            rv['suffix-1'] = word
        elif word_len == 2:
            rv['prefix-1'] = word[:1]
        elif word_len in [3, 4]:
            rv['suffix-2'] = word[-2:]
            rv['prefix-2'] = word[:2]
        else:
            rv['suffix-3'] = word[-3:]
            rv['prefix-3'] = word[:3]
            rv['last_upper'] = word[-1].isupper()
            rv['contains_digit'] = bool(re.search(r"\d", word))
            rv['contains_upper'] = bool(re.search(r"[A-Z]", word[1:]))
            # rv['is_alpha'] = word.isalpha()
            # rv['is_digit'] = word.isdigit()
            # rv['all_upper'] = word.upper() == word
            # rv['all_lower'] = word.lower() == word

        rv['is_gen'] = word in self._geneNames
        rv['is_gen2'] = self._genesDict[word] if word in self._genesDict else ''
        # rv['stopword'] = word in self._stopwords
        # rv['norm_gen'] = extremelyNormalize(word) in self._normGens
        # rv['pos_tag'] = nltk.pos_tag(word)

        return rv
