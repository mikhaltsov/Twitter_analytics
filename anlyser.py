from config import MONGO_HOST
import auth_data
from pymongo import MongoClient
from flair.models import TextClassifier
from flair.data import Sentence


# Connect to MongoDB host
client = MongoClient(MONGO_HOST, username=auth_data.username, password=auth_data.password)
# Use defined database
db = client.twitter_analytics
collection = db.tweets
tweets = collection.find(limit=50)
classifier = TextClassifier.load('en-sentiment')

for tweet in tweets:
    sentence = Sentence(tweet.text)
    classifier.predict(sentence)
    # print tweet with predicted labels
    print(sentence + '---' + sentence.labels)
