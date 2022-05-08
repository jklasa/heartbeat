import os
from argparse import ArgumentParser, FileType
from typing import Dict

import yaml
from common.logger import log
from common.producer import Producer
from tweet.tweet import Tweet
from twitter_ingest import TwitterIngest


def main(config: Dict, bearer_token: str) -> None:
    producer = Producer(
        topic=config["topics"]["out"],
        config_file=config["configs"]["kafka"],
        registry=config["configs"]["registry"],
        data=Tweet,
        do_callback=True,
    )

    # Set up stream
    with open(config["configs"]["rules"]) as file:
        rules = file.readlines()
        task = rules[0].rstrip()[1:]
        rules = [line.rstrip() for line in rules[1:]]

    stream = TwitterIngest(task, producer, bearer_token)

    current_rules = stream.get_rules()
    log.info(f"Current rules: {current_rules}")
    stream.delete_rules([rule.id for rule in current_rules.data])

    for rule in rules:
        stream.add_rules(tweepy.StreamRule(rule))
    thread = stream.filter(tweet_fields=["id", "text", "created_at"])

    stream.poll()


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument(
        "--bearer",
        type=str,
        help="Twitter OAuth bearer token. Required. Can be set by ENV[BEARER_TOKEN].",
    )
    parser.add_argument(
        "--config",
        type=FileType,
        default="config/ingest.yaml",
        help="Ingest config file.",
    )
    args = parser.parse_args()

    if args.bearer is None:
        if "BEARER_TOKEN" not in os.environ:
            raise EnvironmentError("Could not find BEARER_TOKEN")
        bearer = os.environ["BEARER_TOKEN"]

    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    main(config, bearer)
