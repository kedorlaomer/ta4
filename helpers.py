# encoding: utf-8


# projects sentence's elements on their first component
def stripClassifications(sentence):
    return [x[0] for x in sentence]


# returns the first n proper prefixes of string, prefixed with "^" to mark it
# as prefix
def prefixes(s, n=4):
    return ["^" + s[:i] for i in range(1, n + 1)]


# similar to prefixes
def suffixes(s, n=4):
    return [s[i:] + "$" for i in range(len(s) - n, len(s))]


# which of these tags tend to be contained in genes?
def isNominalTag(tag):
    return tag in [
        '-NONE-', ':', 'CD', 'JJ', 'JJR', 'JJS', 'LS', 'NN', 'NNP', 'NNPS',
        'NNS', 'SYM',
    ]


# which tags denote verbs?
def isVerbalTag(tag):
    return tag in ["VBG", "VBN", "VBD", "VBP", "VBZ"]

def writeCorpus(l):
	for i in enumerate(l):
		trainF = open('train'+str(i[0]),'w')
		testF = open('test'+str(i[0]),'w')
		for line in i[1][0]:
			for pair in line:
				trainF.write(pair[0]+'\t'+pair[1]+'\n')
			trainF.write('\n')
		for line in i[1][1]:
			for pair in line:
				testF.write(pair[0]+'\t'+pair[1]+'\n')
			testF.write('\n')
		trainF.close()
		testF.close()