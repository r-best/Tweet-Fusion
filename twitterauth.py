import tweepy
import json

def authenticate():
    # Read in the JSON file that contains the API keys for Twitter
    keys = json.loads(open('data/keys.json').read())

    # Initialize Twitter API with keys from JSON file
    auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
    auth.set_access_token(keys['access_token'], keys['access_token_secret'])
    return tweepy.API(auth)