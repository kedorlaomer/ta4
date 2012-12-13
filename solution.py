#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys

from helpers import stripClassifications
from features import Features
from random import shuffle

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

def makeCrossValidationFiles(f):
    sentences = readSentences(f)
    aux = []
    for i in sentences:
        aux.append(i)
    sentences = aux
    shuffle(sentences)

    for i in range(5):
        if i == 4:
            test = sentences[i*(len(sentences)/5):len(sentences)]
        else : 
            test = sentences[i*(len(sentences)/5):(i+1)*(len(sentences)/5)]
 
        train = sentences[0 : i*(len(sentences)/5)] + sentences[(i+1)*(len(sentences)/5):len(sentences)] 
        yield (train,test)
    


def getUniqueTokens(filename):
    with open(filename) as f:
        return list(set([
            line.strip() for line in f.xreadlines()
        ]))


# Returns a list of (featureSet, label) pairs from file f using
# featureExtractor to find the featureSet. If verbose, then we
# print a progress bar.
def readForTraining(f, featureExtractor, verbose=False):
    rv = []
    i = 0
    for sentence in readSentences(f):
        # sentence contains classifications which the feature extractor
        # shouldn't see
        featureSet = featureExtractor.featuresForSentence(stripClassifications(sentence))
        # but the result should contain them as second element
        pair = zip(featureSet, map(lambda x: x[1], sentence))
        rv += pair
        i += 1

        if verbose:
            if i & 2047 == 0: print "*"
            elif i & 63 == 0: print ":"
            else: sys.stdout.write('.')
            sys.stdout.flush()
    return rv


def solution():
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")
    features = Features(stopwords, geneNames)
    with open("goldstandard2.iob") as f:
        data = readForTraining(f, features, verbose=True)
        return data
        # crossValFile = makeCrossValidationFiles(f)
        # for x in crossValFile:
        #     print type(x)
        #     print x[0][0]
        #     break

if __name__ == '__main__':
    pass
    solution()
