import time

import tweepy
from common.logger import log
from common.producer import Producer
from common.tweet import Tweet


class TwitterIngest(tweepy.StreamingClient):
    def __init__(
        self,
        task: str,
        topic: str,
        producer: Producer,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.task = task
        self.topic = topic
        self.producer = producer

    def on_tweet(self, tweet):
        payload = Tweet(tweet.created_at.timestamp(), tweet.text, self.task)
        self.producer.produce(key=tweet.id, value=payload)

    def poll(self) -> None:
        while True:
            time.sleep(3)
            self.producer.poll(3)
