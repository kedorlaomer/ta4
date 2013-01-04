#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys

from nltk import pos_tag
from nltk.classify import ConditionalExponentialClassifier
from helpers import stripClassifications,writeCorpus,isNominalTag,isVerbalTag
from features import Features
from random import shuffle, random

# reads an IOB file and „yield“s every sentence as a list of
# pairs (token, classification), where all „I“-type
# classifications are changed to „B“ (which is easy to revert)
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
            if classification[0] == 'I':
                    classification = 'B' + classification[1:]
            accu.append((token, classification))

    if len(accu) > 0: # final sentence
        yield accu

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

def betweenProteins(sentence,position):
    if position > 0 and position < len(sentence):
        return (sentence[position-1][1]!= 'O' and sentence[position+1][1]!= 'O')
    elif position == 0:
        return sentence[position+1][1] != 'O'
    else: 
        return sentence[position-1][1] != 'O'


# a list of sentences, binding two proteins separated by a token
# if the token is not a stopword or a verb
def postProcessing(sentences,stopwords):
    for sentence in sentences:
        posTag = [y[1] for y in pos_tag(stripClassifications(sentence))]
        for (position,(token,tag)) in enumerate(sentence):
            if tag != 'O':
                if position > 0:
                    if (sentence[position-1][1] != 'O'):
                        tag = 'I-protein'
                    else:
                        tag = 'B-protein'
                else:
                    #if it is the first occurrence of a protein put the B-Protein tag
                    tag = 'B-protein'
                if token in stopwords:
                    print 'wrong tag -> stopword and protein'
                    tag = 'O'
            else: 
                if token not in stopwords and isNominalTag(posTag[position]) and betweenProteins(sentence,position):
                    print 'wrong tag?? -> between two proteins and not a stopword'
                    tag = 'I-protein'

            sentence[position] = (token, tag)
        yield sentence


def writeSentences(sentences,f):
    for sentence in sentences:
        for line in sentence:
            f.write(line[0]+'\t'+line[1])
        f.write('\n')

# format of data: list as returned by readForTraining
def trainConditionalExponentialClassifier(data):   
    data = [x for y in data for x in y]
    classi = ConditionalExponentialClassifier.train(data,
        algorithm='IIS', max_iter=3)
    return classi

def testClassifier(classifier, features, data):
    allFeatures = [features.featuresForWord(token) for token in data]
    classifications = [classifier.classify(featureset)
        for featureset in allFeatures]
    data = zip(data, classifications)
    return [x for x in postProcessing([data], stopwords)][0]

def solution():
    global stopwords
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")
    features = Features(stopwords, geneNames)
    with open("train0") as f:
        data = readForTraining(f, features, verbose=True)
        classi = trainConditionalExponentialClassifier([x for x in data])
        with open("test0") as f2:
            data = [y for x in readSentences(f2) for y in x]
            data = testClassifier(classi, features, stripClassifications(data))
            writeIOB(data, "eval0")
        #crossValFile = makeCrossValidationFiles(f)
        #writeCorpus(crossValFile)

if __name__ == '__main__':
    classi, data = solution()
