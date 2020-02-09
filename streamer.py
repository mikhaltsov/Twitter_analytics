from config import MONGO_HOST, track, languages, days_to_keep
import auth_data
import tweepy
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os

auth = tweepy.OAuthHandler(auth_data.API_key, auth_data.API_secret_key)
auth.set_access_token(auth_data.access_token, auth_data.access_token_secret)

api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        # Connect to MongoDB host
        client = MongoClient(MONGO_HOST, username=auth_data.username, password=auth_data.password)
        # Use defined database
        db = client.twitter_analytics
        collection = db.tweets

        gen_time = datetime.utcnow() - timedelta(days=days_to_keep)
        del_to_id = ObjectId.from_datetime(gen_time)

        if from_creator(status):
            try:
                if hasattr(status, "extended_tweet"):
                    text = deEmojify(status.extended_tweet["full_text"])
                else:
                    text = deEmojify(status.text)
                collection.insert_one({'created_at': status.created_at,
                                       'user_id': status.id,
                                       'user_name': status.user.name,
                                       'user_screen_name': status.user.screen_name,
                                       'location': status.user.location,
                                       'text': text,
                                       'reply_count': status.reply_count,
                                       'retweet_count': status.retweet_count
                                       }
                                      )
                print(text)
            except Exception:
                pass
        # collection.delete_many({"_id": {"$lte": del_to_id}})

    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False


def from_creator(status):
    if hasattr(status, 'retweeted_status'):
        return False
    elif status.in_reply_to_status_id != None:
        return False
    elif status.in_reply_to_screen_name != None:
        return False
    elif status.in_reply_to_user_id != None:
        return False
    else:
        return True

def deEmojify(text):
    '''
    Strip all non-ASCII characters to remove emoji characters
    '''
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None


if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(track=track, languages=languages)
