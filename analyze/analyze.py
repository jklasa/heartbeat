import time
from argparse import ArgumentParser, FileType
from typing import Dict

import yaml
from common.consumer import Consumer
from common.logger import log
from common.producer import Producer
from sentiment.sentiment import Sentiment
from sentiment_analyzer import SentimentAnalyzer
from tweet.tweet import Tweet


def main(config: Dict) -> None:
    # Set up consumer
    consumer = Consumer(
        config_file=config["configs"]["kafka"],
        registry=config["configs"]["registry"],
        data=Tweet,
    )
    consumer.subscribe([config["topics"]["in"]])

    # Set up producer
    producer = Producer(
        topic=config["topics"]["out"],
        config_file=config["configs"]["kafka"],
        registry=config["configs"]["registry"],
        to_dict=Tweet.to_dict,
        do_callback=True,
    )

    # Set up sentiment analysis
    analyzer = SentimentAnalyzer()

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue

        tweet = msg.value()
        if tweet is not None:
            negative, neutral, positive = analyzer.score(tweet.content)
            sentiment = Sentiment(
                task=tweet.task,
                time=tweet.time,
                pos=positive,
                neu=neutral,
                neg=negative,
            )
            producer.produce(key=msg.key(), value=sentiment)
        producer.poll(1.0)
            


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=FileType,
        default="config/analyzer.yaml",
        help="Analyzer config file.",
    )
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    main(config)
