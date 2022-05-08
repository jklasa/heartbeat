import time

import tweepy

from common.data.tweet.tweet import Tweet
from common.logger import log
from common.producer import Producer


class TwitterIngest(tweepy.StreamingClient):
    def __init__(
        self,
        task: str,
        producer: Producer,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.task = task
        self.producer = producer

    def on_tweet(self, tweet):
        payload = Tweet(self.task, tweet.text, tweet.created_at.timestamp())
        self.producer.produce(key=tweet.id, value=payload)

    def poll(self) -> None:
        while True:
            time.sleep(3)
            self.producer.poll(3)
