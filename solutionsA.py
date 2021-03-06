import math
import nltk
import time

# Constants to be used by you when you fill the functions
START_SYMBOL = '*'
STOP_SYMBOL = 'STOP'
MINUS_INFINITY_SENTENCE_LOG_PROB = -1000

# TODO: IMPLEMENT THIS FUNCTION
# Calculates unigram, bigram, and trigram probabilities given a training corpus
# training_corpus: is a list of the sentences. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function outputs three python dictionaries, where the keys are tuples expressing the ngram and the value is the log probability of that ngram
def calc_probabilities(training_corpus):
    unigram_p = {}
    bigram_p = {}
    trigram_p = {}
    
    num_sent = len(training_corpus)

    # Store the counts of unigram, bigram and trigram
    unigram_count = {}
    bigram_count = {}
    trigram_count = {}
    
    for item in training_corpus:
	sentence = (START_SYMBOL+' '+item.strip()+' '+STOP_SYMBOL).split(' ')
	
	# Count the unigram
	for token in sentence:
	    if token in unigram_count:
		unigram_count[token] += 1
	    else:
		unigram_count[token] = 1
	
	# Count the bigram
	bigram_tmp = nltk.bigrams(sentence)
	for bigram in bigram_tmp:
	    if bigram in bigram_count:
		bigram_count[bigram] += 1
	    else:
		bigram_count[bigram] = 1
	bigram_count[(START_SYMBOL, START_SYMBOL)] = num_sent

	# Count the trigram
	trigram_tmp = nltk.trigrams(sentence)
	trigram = (START_SYMBOL, START_SYMBOL, sentence[1])
	if trigram in trigram_count:
	    trigram_count[trigram] += 1
	else:
	    trigram_count[trigram] = 1
	for trigram in trigram_tmp:
	    if trigram in trigram_count:
		trigram_count[trigram] += 1
	    else:
		trigram_count[trigram] = 1

    # Count the total number of words in corpus, without START_SYMBOL but include STOP_SYMBOL
    n = 0
    for unigram in unigram_count:
	n += unigram_count[unigram]
    n -= num_sent
    log_n = math.log(n,2)
    for unigram in unigram_count:
	unigram_p[(unigram,)] = math.log(unigram_count[unigram],2) - log_n
    del unigram_p[(START_SYMBOL,)]

    for bigram in bigram_count:
	bigram_p[bigram] = math.log(bigram_count[bigram],2) - math.log(unigram_count[bigram[0]],2)
    del bigram_p[(START_SYMBOL, START_SYMBOL)]

    for trigram in trigram_count:
	trigram_p[trigram] = math.log(trigram_count[trigram],2) - math.log(bigram_count[trigram[:2]],2)

    return unigram_p, bigram_p, trigram_p

# Prints the output for q1
# Each input is a python dictionary where keys are a tuple expressing the ngram, and the value is the log probability of that ngram
def q1_output(unigrams, bigrams, trigrams, filename):
    # output probabilities
    outfile = open(filename, 'w')

    unigrams_keys = unigrams.keys()
    unigrams_keys.sort()
    for unigram in unigrams_keys:
        outfile.write('UNIGRAM ' + unigram[0] + ' ' + str(unigrams[unigram]) + '\n')

    bigrams_keys = bigrams.keys()
    bigrams_keys.sort()
    for bigram in bigrams_keys:
        outfile.write('BIGRAM ' + bigram[0] + ' ' + bigram[1]  + ' ' + str(bigrams[bigram]) + '\n')

    trigrams_keys = trigrams.keys()
    trigrams_keys.sort()    
    for trigram in trigrams_keys:
        outfile.write('TRIGRAM ' + trigram[0] + ' ' + trigram[1] + ' ' + trigram[2] + ' ' + str(trigrams[trigram]) + '\n')

    outfile.close()


# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence
# ngram_p: python dictionary of probabilities of uni-, bi- and trigrams.
# n: size of the ngram you want to use to compute probabilities
# corpus: list of sentences to score. Each sentence is a string with tokens separated by spaces, ending in a newline character.
# This function must return a python list of scores, where the first element is the score of the first sentence, etc. 
def score(ngram_p, n, corpus):
    scores = []
    
    for item in corpus:
	sentence = (START_SYMBOL + ' ' + item.strip() + ' ' + STOP_SYMBOL).split()
	score_cur = 0
	tokens = []
	if n == 1:
	    for i in xrange(1, len(sentence)):
		tokens.append((sentence[i],))
	elif n == 2:
	    tokens = nltk.bigrams(sentence)
	else:
	    tokens = nltk.trigrams([START_SYMBOL]+sentence)
	for token in tokens:
	    if token not in ngram_p:
		score_cur = MINUS_INFINITY_SENTENCE_LOG_PROB
		break
	    score_cur += ngram_p[token]
	scores.append(score_cur)
	    	
    return scores

# Outputs a score to a file
# scores: list of scores
# filename: is the output file name
def score_output(scores, filename):
    outfile = open(filename, 'w')
    for score in scores:
        outfile.write(str(score) + '\n')
    outfile.close()

# TODO: IMPLEMENT THIS FUNCTION
# Calculates scores (log probabilities) for every sentence with a linearly interpolated model
# Each ngram argument is a python dictionary where the keys are tuples that express an ngram and the value is the log probability of that ngram
# Like score(), this function returns a python list of scores
def linearscore(unigrams, bigrams, trigrams, corpus):
    scores = []
    for item in corpus:
	score_tmp = 0
	uni_cur = (item.strip()+' '+STOP_SYMBOL).split()
	bi_cur = list(nltk.bigrams([START_SYMBOL]+uni_cur))
	tri_cur = list(nltk.trigrams([START_SYMBOL, START_SYMBOL]+uni_cur))
	for i in xrange(len(uni_cur)):
	    if ((uni_cur[i],) in unigrams) and (bi_cur[i] in bigrams) and (tri_cur[i] in trigrams):
		tmp = math.pow(2, unigrams[(uni_cur[i],)]) + math.pow(2, bigrams[bi_cur[i]]) + math.pow(2, trigrams[tri_cur[i]])
	    else:
		score_tmp = MINUS_INFINITY_SENTENCE_LOG_PROB
		break
	    tmp = math.log(tmp/3,2)
	    score_tmp += tmp
	scores.append(score_tmp)

    return scores

DATA_PATH = 'data/'
OUTPUT_PATH = 'output/'

# DO NOT MODIFY THE MAIN FUNCTION
def main():
    # start timer
    time.clock()

    # get data
    infile = open(DATA_PATH + 'Brown_train.txt', 'r')
    corpus = infile.readlines()
    infile.close()

    # calculate ngram probabilities (question 1)
    unigrams, bigrams, trigrams = calc_probabilities(corpus)

    # question 1 output
    q1_output(unigrams, bigrams, trigrams, OUTPUT_PATH + 'A1.txt')

    # score sentences (question 2)
    uniscores = score(unigrams, 1, corpus)
    biscores = score(bigrams, 2, corpus)
    triscores = score(trigrams, 3, corpus)

    # question 2 output
    score_output(uniscores, OUTPUT_PATH + 'A2.uni.txt')
    score_output(biscores, OUTPUT_PATH + 'A2.bi.txt')
    score_output(triscores, OUTPUT_PATH + 'A2.tri.txt')

    # linear interpolation (question 3)
    linearscores = linearscore(unigrams, bigrams, trigrams, corpus)

    # question 3 output
    score_output(linearscores, OUTPUT_PATH + 'A3.txt')

    # open Sample1 and Sample2 (question 5)
    infile = open(DATA_PATH + 'Sample1.txt', 'r')
    sample1 = infile.readlines()
    infile.close()
    infile = open(DATA_PATH + 'Sample2.txt', 'r')
    sample2 = infile.readlines()
    infile.close() 

    # score the samples
    sample1scores = linearscore(unigrams, bigrams, trigrams, sample1)
    sample2scores = linearscore(unigrams, bigrams, trigrams, sample2)

    # question 5 output
    score_output(sample1scores, OUTPUT_PATH + 'Sample1_scored.txt')
    score_output(sample2scores, OUTPUT_PATH + 'Sample2_scored.txt')

    # print total time to run Part A
    print "Part A time: " + str(time.clock()) + ' sec'

if __name__ == "__main__": main()
