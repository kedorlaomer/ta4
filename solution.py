#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8
from pylab import *
import nltk
import nltk.tag
from collections import defaultdict

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

# returns the first n proper prefixes of string, prefixed with
# "^" to mark it as prefix
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

# Returns a list of dictionaries, one for each token in sentence
# (which should be a list of strings). The keys are names of
# features, the values are bools
def featuresForSentence(sentence):
    rv = range(len(sentence))
    tagged = nltk.pos_tag(sentence)
    for (i, (tag, token)) in enumerate(tagged):
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
            d["pre-nominal"] = isNominalTag(tagged[i-1][1]
            d["pre-verba"] = isVerbalTag(tagged[i-1][1]

################################################################
########################### PROGRAM ############################
################################################################

with open("goldstandard2.iob") as f:
    posTags = defaultdict(lambda: 0)
    for s in readSentences(f):
        for (token, tag) in nltk.pos_tag(stripClassifications(s)):
            if posTags[tag] < 20:
                print "%-15s %s" % (token, tag)
                posTags[tag] += 1

    print "This is a list of POS tags:"
    for tag in posTags:
        print tag
