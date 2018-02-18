from datetime import datetime
import re

def get_last_update_time():
    date_file = open('data/lastupdate.txt', 'r+')
    temp = re.split(' |-|:|\\.', date_file.readline())
    temp = [int(x) for x in temp]
    return datetime(temp[0], temp[1], temp[2], temp[3] + 4, temp[4], temp[5])


def set_last_update_time(new_update_time):
    date_file = open('lastupdate.txt', 'r+')
    date_file.seek(0)
    date_file.write(str(new_update_time))
    date_file.truncate()
    date_file.close()


# Constants
BOT_NAME = 'tweetfuser'

# Read last update time from file
last_update = get_last_update_time()
print("LAST UPDATE: "+str(last_update))

# Read in the JSON file that contains the API keys for Twitter
keys = json.loads(open('data/keys.json').read())

# Initialize Twitter API with keys from JSON file
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

def get_new_tweets():
    new_tweets = api.search(q='@'+BOT_NAME, rpp=100, show_user=1, include_entities=1)
    new_tweets[:] = [x for x in new_tweets if tweet.created_at < last_update and x.user.screen_name != BOT_NAME]
    return new_tweets

# Save new "last updated" time to save to file at end
new_update_time = datetime.now()

tweets = get_new_tweets()
for tweet in tweets:
    reply_mention = '@' + tweet.user.screen_name + ' '
    tweet_mentions = [x.screen_name for x in tweet.entities.user_mentions]
    if BOT_NAME in tweet_mentions:
        tweet_mentions.remove(BOT_NAME)
    if len(tweet_mentions) == 0:
        api.update_status(reply_mention + "It looks like you didnt mention anyone in this tweet for me to use", in_reply_to_status_id=tweet.id)
    

set_last_update_time()