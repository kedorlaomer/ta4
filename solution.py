#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

from pprint import pprint
from collections import defaultdict

from helpers import stripClassifications
from features import Features


# reads an IOB file and „yield“s every sentence as a list of
# pairs (token, classification)
def readSentences(f):
    accu = []
    for l in f.xreadlines():
        line = l.strip()
        contents = line.split("\t")
        if len(contents) != 2:
            if len(accu) > 0:
                yield accu
                accu = []
        else:
            token, classification = contents
            accu.append((token, classification))


def getUniqueTokens(filename):
    with open(filename) as f:
        return list(set([
            line.strip() for line in f.xreadlines()
        ]))


def solution():
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")

    features = Features(stopwords, geneNames)

    with open("goldstandard2.iob") as f:
        # posTags = defaultdict(lambda: 0)
        i = 0
        for s in readSentences(f):
            if i >= 5:
                break
            i += 1

            pprint(
                features.featuresForSentence(stripClassifications(s))
            )


if __name__ == '__main__':
    solution()
