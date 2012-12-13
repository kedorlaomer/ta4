#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys
import random

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

    tokenCount = 0
    prevFeatures = {}
    with open(train_set_filename) as f:
        for line in f.xreadlines():
            line = line.strip()
            contents = line.split("\t")

            if len(contents) == 2:
                token, classification = contents

                currFeatures = features.featuresForWord(token)
                currFeatures.update(prevFeatures)
                featuresets.append((
                    currFeatures, classification
                ))

                prevFeatures.clear()
                for k, v in currFeatures.iteritems():
                    if not k.startswith('$prev_'):
                        prevFeatures['$prev_%s' % k] = v
                prevFeatures['$prev_class'] = classification
            else:
                prevFeatures.clear()

            if tokenCount % 10000 == 0:
                print tokenCount
            tokenCount += 1

    tokenCount = len(featuresets)
    print tokenCount  # 352948

    train_set = []
    test_set = []
    coeff = 2 / 3.0
    for i in xrange(tokenCount):
        if random.random() > coeff:
            test_set.append(featuresets[i])
        else:
            train_set.append(featuresets[i])

    # train_set_size = int(tokenCount * 0.67)
    # train_set = featuresets[:train_set_size]
    # test_set = featuresets[train_set_size:]
    # dev_set = featuresets[int(train_set_size * 0.99):train_set_size]

    print len(train_set)
    print len(test_set)
    # print len(dev_set)

    classifier = NaiveBayesClassifier.train(train_set)
    print "Trained"
    print nltk_classify.accuracy(classifier, test_set)
    # print classifier.show_most_informative_features(20)

    # --------------------------dev
    # print nltk_classify.accuracy(classifier, dev_set), "<- Dev"
    # errors = []
    # for (feature, tag) in dev_set:
    #     guess = classifier.classify(feature)
    #     if guess != tag:
    #         errors.append((tag, guess, feature))
    # for (tag, guess, feature) in sorted(errors):
    #     print 'correct=%-8s guess=%-8s feature=%-30s' % (tag, guess, feature)
    # --------------------------dev


def classify(classify_set_file):
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
