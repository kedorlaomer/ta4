#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys

from nltk import NaiveBayesClassifier
from nltk import classify as nltk_classify

# from helpers import stripClassifications
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


def train(train_set_filename):
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")

    featuresets = []
    features = Features(stopwords, geneNames)

    with open(train_set_filename) as f:
        tokenCount = 0
        for line in f.xreadlines():
            line = line.strip()
            contents = line.split("\t")
            if len(contents) == 2:
                token, classification = contents
                featuresets.append((
                    features.featuresForWord(token), classification,
                ))

            if tokenCount % 1000 == 0:
                print tokenCount
            tokenCount += 1

    tokenCount = len(featuresets)
    print tokenCount  # 352948

    train_set_size = int(tokenCount * 0.67)
    train_set = featuresets[:train_set_size]
    test_set = featuresets[train_set_size:]

    print len(train_set)
    print len(test_set)

    classifier = NaiveBayesClassifier.train(train_set)
    print "Trained"
    print nltk_classify.accuracy(classifier, test_set)
    print classifier.show_most_informative_features(10)


def classify(classify_set_file):
    pass


def solution():
    pass


if __name__ == '__main__':
    args = sys.argv[1:]
    if '-t' in args:
        train(args[args.index('-t') + 1])
    elif '-c' in args:
        classify(args[args.index('-c') + 1])
    else:
        print """
            Usage:
            -t\t<train_set_filename>;
            -c\t<classify_set_file>;
        """
