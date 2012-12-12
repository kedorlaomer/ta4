#!/vol/fob-vol3/mi12/adleralq/gentoo/usr/bin/python
# encoding: utf-8

import sys
from pprint import pprint
from collections import defaultdict

from nltk import NaiveBayesClassifier
from nltk import classify as nltk_classify

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


def train(train_set_filename):
    stopwords = getUniqueTokens("english_stop_words.txt")
    geneNames = getUniqueTokens("genenames-2.txt")
    print "Read"

    features = Features(stopwords, geneNames)

    delimiters = []
    for gene in geneNames:
        delimiters.extend([
            x for x in gene if not x.isalnum()
        ])
    delimiters = list(set(delimiters))

    featuresets = []
    for gene in geneNames:
        gene += "\n"
        curr_gene = ""
        firstFound = False
        for c in gene:
            if gene != "\n":
                curr_gene += c
            if c in delimiters:
                if firstFound:
                    classification = "I-protein"
                else:
                    classification = "B-protein"
                    firstFound = True
                featuresets.append((
                    features.featuresForWord(curr_gene),
                    classification,
                ))
                curr_gene = ""

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

            if tokenCount % 10000 == 0:
                print tokenCount
            tokenCount += 1

    tokenCount = len(featuresets)
    print tokenCount  # 352948

    train_set_size = int(tokenCount * 0.75)
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
