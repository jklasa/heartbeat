import logging
import os
import struct
import time
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from typing import Dict

import tweepy
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import Serializer, SerializationError


class LongSerializer(Serializer):
    def __call__(self, obj, ctx):
        if obj is None:
            return None
        try:
            return struct.pack(">Q", obj)
        except struct.error as e:
            raise SerializationError(str(e))


class Tweet(object):
    def __init__(self, time: int, content: str, task: str):
        self.time = time
        self.content = content
        self.task = task

    def to_dict(self, ctx):
        return dict(time=self.time, content=self.content, task=self.task)


class TwitterIngest(tweepy.StreamingClient):
    def __init__(self, task: str, config: Dict, *args, do_callback: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = task

        schema_str = """
        {
            "name": "tweet",
            "type": "record",
            "fields": [
                {
                    "name": "time", 
                    "type": {"type": "int", "logicalType": "timestamp-millis"}
                },
                {"name": "content", "type": "string"},
                {"name": "task", "type": "string"}
            ]
        }
        """

        # Create Producer instance
        schema_registry_conf = {
            "url": "http://schemaregistry.heartbeat.svc.cluster.local:8081"
        }
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        avro_serializer = AvroSerializer(
            schema_registry_client, schema_str, Tweet.to_dict
        )
        config |= {
            "value.serializer": avro_serializer,
            "key.serializer": LongSerializer(),
        }
        self.producer = SerializingProducer(config)

        if do_callback:
            self.callback = TwitterIngest.delivery_callback
        else:
            self.callback = None

    def on_tweet(self, tweet):
        payload = Tweet(tweet.created_at.timestamp(), tweet.text, self.task)
        self.producer.produce(
            topic="ingest", key=tweet.id, value=payload, on_delivery=self.callback
        )

    def poll(self) -> None:
        while True:
            time.sleep(3)
            self.producer.poll(3)

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


def main(config_file: FileType,
         rules_file: FileType, 
         log_level: str, 
         bearer_token: str,
) -> None:
    # Parse the configuration.
    # https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    with open(config_file) as file:
        config_parser.read_file(file)
    config = dict(config_parser["default"]) | dict(config_parser["producer"])

    # Set up logging
    level = init_logging(log_level.lower())

    # Set up stream
    with open(rules_file) as file:
        rules = file.readlines()
        task = rules[0].rstrip()[1:]
        rules = [line.rstrip() for line in rules[1:]]

    stream = TwitterIngest(task, config, bearer_token, do_callback=level == 0)

    current_rules = stream.get_rules()
    logging.info(f"Current rules: {current_rules}")
    stream.delete_rules([rule.id for rule in current_rules.data])

    for rule in rules:
        stream.add_rules(tweepy.StreamRule(rule))
    thread = stream.filter(tweet_fields=["id", "text", "created_at"])

    stream.poll()


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument(
        "--use-env", 
        action="store_true", 
        help="Use environment variables for config" \
             "(BEARER_TOKEN, PRODUCER_CONFIG, LOG_LEVEL, RULES_CONFIG).",
    )
    parser.add_argument(
        "--bearer",
        type=str,
        help="Twitter OAuth bearer token.",
    )
    parser.add_argument(
        "--config",
        default="/config/ingest.ini",
        help="Producer config file.",
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        default="DEBUG", 
        help="Logging output level."
    )
    parser.add_argument(
        "--rules",
        default="/config/ingest.rules",
        help="Twitter filter config file.",
    )
    parser.set_defaults(use_env=False)
    args = parser.parse_args()

    if args.use_env:
        bearer = os.environ["BEARER_TOKEN"]
        config = os.environ["PRODUCER_CONFIG"]
        level = os.environ["LOG_LEVEL"]
        rules = os.environ["RULES_CONFIG"]

        main(config, rules, level, bearer)
    else:
        main(args.config, args.rules, args.log_level, args.bearer)
