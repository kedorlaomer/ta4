#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys

from helpers import stripClassifications,writeCorpus
from features import Features
from random import shuffle, random

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

# „yields“ 5 pairs of (training, test) where ⅕ of the data are
# randomly chosen to be test-Data
def makeCrossValidationFiles(f):
    sentences = readSentences(f)
    aux = []
    for i in sentences:
        aux.append(i)
    sentences = aux
    shuffle(sentences)

    print len(sentences)
    for i in range(5):
        inter0 = i*(len(sentences)/5)
        inter1 = (i+1)*(len(sentences)/5)

        if i == 4:
            test = sentences[i*(len(sentences)/5):len(sentences)]
            train = sentences[0 : i*(len(sentences)/5)]
        elif i==0:
            test = sentences[i*(len(sentences)/5):(i+1)*(len(sentences)/5)]
            train = sentences[(i+1)*(len(sentences)/5):len(sentences)]   
        else : 
            test = sentences[i*(len(sentences)/5):(i+1)*(len(sentences)/5)]
            train = sentences[0 : i*(len(sentences)/5)] + sentences[(i+1)*(len(sentences)/5):len(sentences)] 
        yield (train,test)
    


def getUniqueTokens(filename):
    with open(filename) as f:
        return list(set([
            line.strip() for line in f.xreadlines()
        ]))


# „yields“ (featureSet, label) pairs from file f using
# featureExtractor to find the featureSet. If verbose, then
# print a progress bar.
def readForTraining(f, featureExtractor, verbose=False):
    i = 0
    for sentence in readSentences(f):
        # sentence contains classifications which the feature extractor
        # shouldn't see
        featureSet = featureExtractor.featuresForSentence(stripClassifications(sentence))
        # but the result should contain them as second element
        pair = zip(featureSet, map(lambda x: x[1], sentence))
        i += 1

        if verbose:
            if i & 2047 == 0: print "*"
            elif i & 63 == 0: print ""
            else: sys.stdout.write('.')
            sys.stdout.flush()
        yield pair

# partitions the list l = [l_1, …, l_n] into a pair (l1, l2),
# where approximately n*epsilon of the l_i end up in l1 and the
# rest in l2
def partitionList(l, epsilon):
    (rv1, rv2) = ([], [])
    for x in l:
        (rv1 if random() < epsilon else rv2).append(x)

    return (rv1, rv2)

def betweenProteins(sentence,position):
    if position > 0 and position < len(sentence):
        return (sentence[position-1][1]!= 'O' and sentence[position+1][1]!= 'O')
    elif position == 0:
        return sentence[position+1][1] != 'O'
    else: 
        return sentence[position-1][1] != 'O'

# post processes a file f, fixing IOB format and 
# binding two proteins separated by a token if the token is not a stopword ¿or a verb?
def postProcessing(f,stopwords):
    for sentence in readSentences(f):
        for (pos,(token,tag)) in enumerate(sentence):
            if tag != 'O':
                if pos > 0:
                    if (sentence[pos-1][1] != 'O'):
                        sentence[1] = 'I-Protein'
                else:
                    #if it is the first occurrence of a protein put the B-Protein tag
                    sentence[1] = 'B-Protein'
                if token in stopwords:
                    print 'wrong tag -> stopword and protein'
                    sentence[1] = 'O'
            else: 
                if token not in stopwords and betweenProteins(sentence,pos):
                    print 'wrong tag?? -> between two proteins and not a stopword'
                    sentence[1] = 'I-Protein'
        yield sentence

def writeSentences(sentences,f):
    for sentence in sentences:
        for line in sentence:
            f.write(line[0]+'\t'+line[1])
        f.write('\n')

def solution():
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")
    features = Features(stopwords, geneNames)
    with open("goldstandard2.iob") as f:
        data = readForTraining(f, features, verbose=True)
        #crossValFile = makeCrossValidationFiles(f)
        #writeCorpus(crossValFile)

if __name__ == '__main__':
    solution()
