from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

#consumer key, consumer secret, access token, access secret.
ckey="ztx0v1EXWgXMyd9vYoMpClroJ"
csecret="3R0NB1lRAMJs5gVmTr5MaV3KGwUCKw65qa8GgAxxeFdxSVRe1s"
atoken="945629418-jIcBCixQWN4Ou2QirRdieqxFjHDgoKlRbZ0SXwON"
asecret="Ck3mXbuNknELWdwjoPVQj6pmtppSRJNV9YjQEu22EfBVW"


class listener(StreamListener):

    def on_data(self, data):

        all_data = json.loads(data)

        tweet = all_data["text"]
        tweet_blob = TextBlob(tweet,analyzer=NaiveBayesAnalyzer())
        print("--->",tweet,tweet_blob.sentiment)
       

    def on_error(self, status):
        print(status)


    
def get_sentiment(sentence):
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, listener())
    
    sentence =TextBlob(sentence)
    sentence = sentence.noun_phrases
    print(sentence)
    twitterStream.filter(languages=["en"],track=sentence, async=True)

if __name__ == '__main__':
    get_sentiment(sentence)
