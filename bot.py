from twitterauth import authenticate
from generator import generate_tweets
import datetime
import re

def get_last_update_time():
    date_file = open('data/lastupdate.txt', 'r+')
    temp = re.split(' |-|:|\\.', date_file.readline())
    temp = [int(x) for x in temp]
    last_update = datetime.datetime(temp[0], temp[1], temp[2], temp[3], temp[4], temp[5])
    return last_update + datetime.timedelta(hours=5)

def set_last_update_time(new_update_time):
    date_file = open('data/lastupdate.txt', 'r+')
    date_file.seek(0)
    date_file.write(str(new_update_time))
    date_file.truncate()
    date_file.close()

# Constants
BOT_NAME = 'tweetfuser'

# Read last update time from file
last_update = get_last_update_time()
print("LAST UPDATE: "+str(last_update))

# Get a Tweepy API object
api = authenticate()

def get_new_tweets():
    new_tweets = api.search(q='@'+BOT_NAME, rpp=100, show_user=1, include_entities=1)
    new_tweets[:] = [x for x in new_tweets if x.created_at > last_update and x.user.screen_name != BOT_NAME]
    return new_tweets

# Save new "last updated" time to save to file at end
new_update_time = datetime.datetime.now()

tweets = get_new_tweets()
for tweet in tweets:
    print tweet.created_at
    reply_mention = '@' + tweet.user.screen_name + ' '
    tweet_mentions = [x['screen_name'] for x in tweet.entities['user_mentions']]
    if BOT_NAME in tweet_mentions:
        tweet_mentions.remove(BOT_NAME)
    if len(tweet_mentions) == 0:
        api.update_status(reply_mention + "It looks like you didnt mention anyone in this tweet for me to use", in_reply_to_status_id=tweet.id)
    generated_tweet = generate_tweets(3, 1, 5, api, tweet_mentions)[0]
    generated_tweet = re.sub("Tweet 1: ", "", generated_tweet)
    print generated_tweet
    api.update_status(reply_mention + generated_tweet, in_reply_to_status_id=tweet.id)
set_last_update_time(new_update_time)