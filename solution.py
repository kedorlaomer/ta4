#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import nltk
import nltk.tag
from collections import defaultdict
from pprint import pprint

# reads an IOB file and „yield“s every sentence as a list of
# pairs (token, classification)
def readSentences(f):
    accu = []
    for l in f.xreadlines():
        line = l.strip()
        contents = line.split("\t")
        if len(contents) < 2:
            if len(accu) > 0:
                yield accu
                accu = []
        else:
            token, classification = contents
            accu.append((token, classification))

# projects sentence's elements on their first component
def stripClassifications(sentence):
    return map(lambda x: x[0], sentence)

# returns the first n proper prefixes of string, prefixed with "^" to mark it
# as prefix
def prefixes(s, n=4):
    return ["^" + s[:i] for i in range(1, n+1)]

# similar to prefixes
def suffixes(s, n=4):
    return [s[i:] + "$" for i in range(len(s)-n, len(s))]

# which of these tags tend to be contained in genes?
def isNominalTag(tag):
    return tag in ["NNP", "NNPS", ":", "NN", "CD", "JJ", "NNS", "JJR", "JJS", "SYM", "-NONE-", "LS"]

# which tags denote verbs?
def isVerbalTag(tag):
    return tag in ["VBG", "VBN", "VBD", "VBP", "VBZ"]

def getUniqueTokens(filename):
    with open(filename) as f:
        return set([
            line.lower().strip() for line in f.xreadlines()
        ])

################################################################
########################### PROGRAM ############################
################################################################

stopwords = getUniqueTokens("english_stop_words.txt")
geneNames = getUniqueTokens("genenames-2.txt")

with open("goldstandard2.iob") as f:
    posTags = defaultdict(lambda: 0)
    i = 0
    for s in readSentences(f):
        if i >= 5:
            break
        i += 1

        pprint(featuresForSentence(stripClassifications(s)))
