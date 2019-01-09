# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 22:26:16 2019

@author: @adriantoto
"""

# twitter bot #

# Libraries
import tweepy 
import nltk.data #honestly idk what is the function of the nltk.data library. I import this library to handle some errors. 
import time
import datetime
import textblob
import matplotlib.pyplot as plt

# NOTE: flush=True is just for running this script
# with PythonAnywhere's always-on task.
# More info: https://help.pythonanywhere.com/pages/AlwaysOnTasks/
print('this is my twitter bot', flush = True)

# tweepy template
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#temp text file
FILE_NAME = 'last_seen_id.txt'

#functions
def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                                last_seen_id,
                                tweet_mode = 'extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        
        # what do you want to do with the tweets 
        if '' in mention.full_text.lower():
            print('found an user', flush=True)
            print('responding back....', flush=True)
            #keyword
            keyword= (mention.full_text.lower()).lstrip("@adriantotobot")
            print(keyword)
            #number of tweets and cursor
            numberOfTweets= 100
            tweets = tweepy.Cursor(api.search, 
                                   q=keyword, 
                                   lang='en').items(numberOfTweets)
            #sentiment variables declaration
            positive = 0
            negative = 0
            neutral = 0
            polarity = 0
            #percentage function
            def calculatePercentage(a,b):
                return 100*float(a)/float(b)
            #the most retweet attributes
            maxRT = 0
            #rt_usermame = ''
            rt_id = 0
            #inspect tweet 
            for tweet in tweets:
                print(tweet.text)
                #counting the retweet
                retweet = tweet.retweet_count
                #changing the most retweet attributes
                if retweet > maxRT:
                    maxRT = retweet
                    rt_id = tweet.id
                    rt_username = tweet.author.screen_name
                #sentiment analysis using textblob
                myAnalysis=textblob.TextBlob(tweet.text)
                polarity += myAnalysis.sentiment.polarity
                if myAnalysis.sentiment.polarity == 0:
                    neutral += 1
                elif myAnalysis.sentiment.polarity > 0.00:
                    positive += 1
                elif myAnalysis.sentiment.polarity < 0.00:
                    negative += 1
            #calculate the percentages
            positive=calculatePercentage(positive,numberOfTweets)
            negative=calculatePercentage(negative,numberOfTweets)
            neutral=calculatePercentage(neutral,numberOfTweets)
            #format numbers digit
            positive=format(positive,'.0f')
            negative=format(negative,'.0f')
            neutral=format(neutral,'.0f')
            #Pie graph
            labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]','Negative [' + str(negative) + '%]']
            sizes=[positive,neutral,negative]
            colors=['green','yellow','red']
            patches,texts=plt.pie(sizes,colors=colors,startangle=90)
            plt.legend(patches,labels,loc="best")
            plt.title('How people are reacting on' + keyword + ' by analyzing ' + str(numberOfTweets) + ' mixed tweets\n' + ' on ' + str(datetime.datetime.now()))   
            plt.axis('equal')
            plt.tight_layout()
            filename = "SentimentAnalysis_of_" + keyword + ".png"
            plt.savefig(filename)
            plt.show()
            #convert to string
            rt_id2 = str(rt_id)
            maxRT2 = str(maxRT)
            #upload to twitter
            api.update_with_media(filename, status= '@' + mention.user.screen_name + ' ' + '\n'
                                  + ' The most retweeted tweet: ' 
                                  + 'https://twitter.com/{}/status/{}'.format(rt_username, rt_id2) + '\n'
                                  + 'with ' + maxRT2 + ' retweets.', in_reply_to_status_id = mention.id)
            #favorite and retweet the mention tweet 
            api.create_favorite(mention.id)
            api.retweet(mention.id) 
while True:
    reply_to_tweets()
