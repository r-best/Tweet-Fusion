from datetime import datetime
from random import random
from twitterauth import authenticate
import tweepy
import json
import sys
import re

def get_user_tweets(R, api, user):
    tweets = []
    try:
        for r in range(1, R+1):
            user_tweets = api.user_timeline(screen_name=user, count=200, page=r)
            for tweet in user_tweets:
                if "RT @" not in tweet.text:
                    try:
                        tweets.append(tweet.text.encode('ascii'))
                    except UnicodeEncodeError:
                        continue
        return tweets
    except tweepy.error.RateLimitError:
        print "Twitter API rate limit exceeded"
        return tweets

def generate_tweets(N, M, R, api, screennames):
    tweets = [] # Array of all tweets from given users
    for user in screennames: # Rest of args should be Twitter screen names
        try:
            # Try to get the given user's tweets and add them to the list
            temp = get_user_tweets(R, api, user)
            tweets.extend(temp)
        except tweepy.error.TweepError: # If error just continue to the next user
            print "Unable to fetch tweets of user '"+str(user)+"', skipping"
            continue

    if len(tweets) == 0:
        print >> sys.stderr, "No tweets were retrieved for the given users"
        sys.stderr.flush()
        sys.exit(0)

    # Build N-grams, (N-1)-grams, and list of tokens
    ngrams = {}
    n1grams = {}
    tokens = []
    for tweet in tweets:
        # For each tweet, add whitespace around its punctuation marks, then 
        # split on whitespace to make an array of all the tokens in the tweet
        tweet = re.sub(r"([\(\)\$\.\!\?,'`\"%&:;])", r" \1 ", tweet)
        tweet = tweet.lower()
        tweet = tweet.split()

        # Skip this tweet if it's not long enough
        if len(tweet) < N:
            continue

        # Add N-1 <start> tags to front of tweet and <end> tags to back
        for n in range(0, N-1):
            tweet = ["<start>"] + tweet + ["<end>"]

        # For each token in the tweet, construct and N-gram and an (N-1)-gram 
        # from it and the respective number of tokens behind it
        for i in range(N-2, len(tweet)):
            # Start by building (N-1)-gram
            n1gram = []
            for n in range(0, N-1):
                n1gram = [tweet[i-n]] + n1gram
            n1gram = " ".join(n1gram)
            if n1gram in n1grams:
                n1grams[n1gram] += 1 # Increment the frequency of the (N-1)-gram
            else:
                n1grams[n1gram] = 1
            # The N-gram is just the (N-1)-gram with the next token back tacked onto the front of it
            ngram = tweet[i-N+1] + " " + n1gram
            if ngram in ngrams:
                ngrams[ngram] += 1 # Increment the frequency of the N-gram
            else:
                ngrams[ngram] = 1
            # Add token to tokens list
            tokens.append(tweet[i])
    # Uniqueify the tokens list
    tokens = list(set(tokens))

    # Calculate those delicious probabilities
    P = {} # A hash of hashes s.t. P[a][b] = P(b|a) = the probability that the next word is b given we've just seen a

    for n1gram in n1grams:
        P[n1gram] = {}
        for token in tokens:
            ngram = n1gram + " " + token
            if ngram in ngrams:
                P[n1gram][token] = float(ngrams[ngram]) / float(n1grams[n1gram])

    # Generate tweets!
    generated_tweets = []
    for m in range(1, M+1):
        # Initialize tweet with N-1 <start> tags
        tweet = ""
        for n in range(0, N-1):
            tweet = tweet + "<start>"
            if n < N-2:
                tweet = tweet + " "

        while "<end>" not in tweet:
            rand = random()
            counter = 0

            # Get the last N-1 words of the current tweet
            lastN1Words = []
            temp = tweet.split()
            for n in range(0, N-1):
                lastN1Words = [temp.pop()] + lastN1Words
            lastN1Words = " ".join(lastN1Words)
            
            for token in tokens:
                if (lastN1Words not in P) or (token not in P[lastN1Words]) or (P[lastN1Words][token] == 0):
                    continue
                counter += P[lastN1Words][token]
                if counter > rand:
                    tweet += " " + token
                    break
        tweet = re.sub(r"\s*<start>\s*", r"", tweet)
        tweet = re.sub(r"\s*<end>", r"", tweet)
        tweet = re.sub(r"\s*'\s*", r"'", tweet)
        tweet = re.sub(r"\s*([,\.\!\?\)])", r"\1", tweet)
        tweet = re.sub(r"(\(\$)\s*", r"\1", tweet)
        tweet = tweet.capitalize()
        generated_tweets.append("Tweet " + str(m) + ": " + tweet)
    return generated_tweets

def main():
    # Remove first command line arg (it's the name of this file)
    sys.argv.pop(0)

    # Constants
    N = 3 # Value of N in N-gram
    M = 100 # Number of tweets to generate
    R = 1 # Number of requests to make per user (fetches 200 tweets per request)
    try:
        N = int(sys.argv.pop(0))
        M = int(sys.argv.pop(0))
        R = int(sys.argv.pop(0))
    except ValueError:
        print >> sys.stderr, "N, M, or R was NaN"
        sys.stderr.flush()
        sys.exit(0)
    generated_tweets = generate_tweets(N, M, R, authenticate(), sys.argv)
    for tweet in generated_tweets:
        print tweet
    print("<ENDOFOUTPUT>")
    sys.stdout.flush()
    

if __name__ == '__main__':
    main()