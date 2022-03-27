import tweepy
from distracker import settings
from transformers import pipeline
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
import sys

#sys.path.append('$HOME/.cargo/bin')

tkn= getattr(settings, "BEARER_TOKEN", None)

#Transformer model for sentiment
sent_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

#GET tweets based on query and return amplification score
def get_tweets(q):
	client = tweepy.Client(bearer_token=tkn)
	query = q+' -is:retweet is:reply lang:en'
	tweets = client.search_recent_tweets(query=query, tweet_fields=['author_id','conversation_id', 'in_reply_to_user_id', 'public_metrics', 'created_at', 'referenced_tweets', 'geo'],  max_results=10)
	conversations =[{'conversation':t['conversation_id'], 'reference':t.referenced_tweets[0]['id']} for t in tweets.data if t['conversation_id']]
	conv_responses = get_message_tree(conversations)
	for i in range(0, len(tweets.data)):
		twt_1 = tweets.data[i].text
		sent1 = sent_model(twt_1)
		twt_2 = conv_responses[i]
		if twt_2[1] is not None:
			sent_21 = sent_model(twt_2[0].data.text)
			sent_22 = sent_model(twt_2[1].data.text)



#Based on a list of conversation ids, return the original message and response if exists
def get_message_tree(conversations):
	conversations =[]
	client = tweepy.Client(bearer_token=tkn)
	for id in conversations:
		print(id)
		if id['conversation'] == id['reference']:
			print(id['conversation'])
			tweet = client.get_tweet(id['conversation'], tweet_fields=['author_id','conversation_id', 'in_reply_to_user_id', 'public_metrics', 'created_at', 'referenced_tweets', 'geo'])
			conversations.append((tweet,None))
		elif id['conversation'] != id['reference']:
			print(id['conversation'])
			tweet_conv = client.get_tweet(id['conversation'], tweet_fields=['author_id','conversation_id', 'in_reply_to_user_id', 'public_metrics', 'created_at', 'referenced_tweets', 'geo'])
			tweet_ref = client.get_tweet(id['reference'], tweet_fields=['author_id','conversation_id', 'in_reply_to_user_id', 'public_metrics', 'created_at', 'referenced_tweets', 'geo'])
			conversations.append((tweet_conv, tweet_ref))
	return conversations
