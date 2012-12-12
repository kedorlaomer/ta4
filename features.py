#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import re

import nltk

from helpers import suffixes, prefixes, isNominalTag, isVerbalTag


# A class for extracting features from sentences.
class Features(object):
    _stopwords = None
    _geneNames = None

    def __init__(self, stopwords, geneNames):
        self._stopwords = stopwords
        self._geneNames = geneNames

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
        return {
            # 'first_letter': word[0],
            # 'last_letter': word[-1],
            # 'last_upper': word[-1].isupper(),
            'tagged': nltk.pos_tag([word])[0][1],
            # 'all_upper': word.isupper(),
        }
