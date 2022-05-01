import logging
import os
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from typing import Dict

import tweepy
from confluent_kafka import Producer


class TwitterIngest(tweepy.StreamingClient):
    def __init__(self, config: Dict, *args, do_callback: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        # Create Producer instance
        self.producer = Producer(config)

        if do_callback:
            self.callback = TwitterIngest.delivery_callback
        else:
            self.callback = None

    def on_tweet(self, tweet):
        self.producer.produce(
            topic="ingest", key=tweet.id, value=tweet, callback=self.callback
        )

    @staticmethod
    def delivery_callback(err: str, msg: str) -> None:
        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently
        # failed delivery (after retries).
        if err:
            logging.error("Message failed delivery: {}".format(err))
        else:
            logging.debug(
                "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(),
                    key=msg.key().decode("utf-8"),
                    value=msg.value().decode("utf-8"),
                )
            )


def init_logging(level: str) -> int:
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    assert level in levels
    logging.basicConfig(
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=levels[level],
    )

    return list(levels.keys()).index(level)


def main(args) -> None:
    # Parse the configuration.
    # https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser["default"])

    # Set up logging
    level = init_logging(config.log_level.lower())

    # OAuth
    bearer_token = os.environ["BEARER_TOKEN"]

    # Set up stream
    with open(args.rules) as file:
        rules = file.readlines()
        rules = [line.rstrip() for line in lines]

    stream = TwitterIngest(bearer_token, do_callback=level == 0)
    for rule in rules:
        stream.add_rules(rule)
    stream.sample()


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument(
        "config",
        type=FileType("r"),
        required=True,
        help="Producer config file.",
        s,
    )
    parser.add_argument(
        "log-level", type=str, default="DEBUG", help="Logging output level."
    )
    parser.add_argument(
        "rules",
        type=FileType("r"),
        required=True,
        help="Twitter filter config file.",
    )
    args = parser.parse_args()

    main(args)
