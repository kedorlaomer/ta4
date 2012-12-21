# encoding: utf-8

import sys
from random import random, shuffle

import cPickle
from os.path import isfile as os_isfile

from nltk import NaiveBayesClassifier
from nltk import classify as nltk_classify

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


# „yields“ n pairs of (training, test) where ⅕ of the data are
# randomly chosen to be test-Data
def makeCrossValidationFiles(f, parts=5):
    sentences = list(readSentences(f))
    shuffle(sentences)

    part_count = len(sentences) / parts
    for i in xrange(parts):
        if i == parts - 1:
            test = sentences[i * part_count:]
        else:
            test = sentences[i * part_count:(i + 1) * part_count]

        train = sentences[:i * part_count] + sentences[(i + 1) * part_count:]
        yield (train, test)


def iterFileTokens(filename):
    if os_isfile(filename):
        with open(filename) as f:
            for line in f.xreadlines():
                line = line.strip()
                contents = line.split("\t")

                if len(contents) == 2:
                    yield contents
    else:
        print "File '%s' don't exists!" % filename


def getFileTokens(filename):
    return list(iterFileTokens(filename))


def getUniqueFileTokens(filename):
    return set(iterFileTokens(filename))


def saveOutput(filename, classifiedTokens):
    with open(filename, "w") as f:
        for token, classification in classifiedTokens:
            f.write("%s\t%s\n" % (token, classification))
    print "Classified output was saved to file '%s'" % filename


def writeCorpus(l):
    # parts?!
    for i, parts in enumerate(l):
        trainF = open('train%s' % i, 'w')
        testF = open('test%s' % i, 'w')

        for line in parts[0]:
            for pair in line:
                trainF.write("%s\t%s\n" % pair)
            trainF.write('\n')
        for line in parts[1]:
            for pair in line:
                testF.write("%s\t%s\n" % pair)
            testF.write('\n')

        trainF.close()
        testF.close()


def dumpClassifier(filename, classifier):
    with open(filename, 'wb') as f:
        cPickle.dump(classifier, f)
    print "Classifier was successfully dumped to file '%s'" % filename


def loadClassifier(filename):
    if not os_isfile(filename):
        print "File '%s' don't exists!" % filename
        return None

    with open(filename) as f:
        classifier = cPickle.load(f)
    return classifier


def train(trainSetFilename, classifierFilename='classifier.classi'):
    stopwords = getUniqueFileTokens("english_stop_words.txt")
    geneNames = getUniqueFileTokens("genenames-2.txt")
    classifiedTokens = getFileTokens(trainSetFilename)
    print "Read"

    features = Features(stopwords, geneNames)
    featuresets = []

    prevClassification = ''
    # tokenCount = 0
    for token, classification in classifiedTokens:
        currFeatures = features.featuresForWord(token)
        if prevClassification:
            currFeatures['prevClassification'] = prevClassification
        prevClassification = classification

        featuresets.append((
            currFeatures, classification,
        ))

        # if tokenCount % 10000 == 0:
        #     print "%s/%s" % (tokenCount, len(classifiedTokens))
        # tokenCount += 1

    # train_set = []
    # test_set = []
    # coeff = 2 / 3.0
    # for i in xrange(tokenCount):
    #     if random() > coeff:
    #         test_set.append(featuresets[i])
    #     else:
    #         train_set.append(featuresets[i])
    # print len(train_set)
    # print len(test_set)

    classifier = NaiveBayesClassifier.train(featuresets)
    # print classifier.show_most_informative_features(10)
    # print nltk_classify.accuracy(classifier, test_set)
    dumpClassifier(classifierFilename, classifier)


def classify(
        classifySetFilename,
        classifierFilename='classifier.data',
        predictFilename='output.predict'
    ):
    classifier = loadClassifier(classifierFilename)
    if not classifier:
        return
    stopwords = getUniqueFileTokens("english_stop_words.txt")
    geneNames = getUniqueFileTokens("genenames-2.txt")
    print "Read"

    features = Features(stopwords, geneNames)
    classifiedTokens = []
    prevClassification = ''

    for token, uselessClassification in iterFileTokens(classifySetFilename):
        del uselessClassification

        currFeatures = features.featuresForWord(token)
        if prevClassification:
            currFeatures['prevClassification'] = prevClassification

        classification = classifier.classify(currFeatures)
        classifiedTokens.append((
            token, classification,
        ))

    saveOutput(predictFilename, classifiedTokens)


def makeCrossValidation(train_set_filename):
    with open(train_set_filename) as f:
        groupped_sentences = makeCrossValidationFiles(f)
        writeCorpus(groupped_sentences)


if __name__ == '__main__':
    args = sys.argv[1:]
    if '-t' in args:
        train(*args[args.index('-t') + 1:])
    elif '-c' in args:
        classify(*args[args.index('-c') + 1:])
    elif '-crossv' in args:
        makeCrossValidation(*args[args.index('-crossv') + 1:])
    else:
        print """
            Usage:
            -t\t<train_set_filename> <classifier_filename>;
            -c\t<classify_set_file> <classifier_filename> <predict_filename>;
        """
