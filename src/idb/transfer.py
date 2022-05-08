import time
from argparse import ArgumentParser
from typing import Dict

from influxdb_client import InfluxDBClient, Point, WriteOptions

from common.consumer import Consumer
from common.data.sentiment.sentiment import Sentiment
from common.logger import log


def main(config: Dict, token: str) -> None:
    # Set up consumer
    consumer = Consumer(
        config_file=config["configs"]["kafka"],
        registry_file=config["configs"]["registry"],
        data=Sentiment,
    )
    consumer.subscribe([config["topics"]["in"]])

    bucket = config["db"]["bucket"]
    with InfluxDBClientAsync(
        url=config["db"]["endpoint"], token=token, org=config["db"]["org"]
    ) as client:
        with client.write_api(
            write_options=WriteOptions(
                batch_size=config["db"]["batch_size"],
                flush_interval=config["db"]["batch_size"],
            )
        ) as write_client:

            while True:
                for i in range(15):
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    sentiment = msg.value()
                    if sentiment is not None:
                        write_client.write(
                            bucket, record=sentiment.make_line(msg.key())
                        )


if __name__ == "__main__":
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument(
        "--token",
        type=str,
        help="InfluxDB Auth Token. Required. Can be set by ENV[IDB_TOKEN].",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/idb.yaml",
        help="Analyzer config file.",
    )
    args = parser.parse_args()

    if args.token is None:
        if "IDB_TOKEN" not in os.environ:
            raise EnvironmentError("Could not find IDB_TOKEN")
        token = os.environ["IDB_TOKEN"]

    with open(args.config, "r") as stream:
        config = yaml.safe_load(stream)

    main(config, token)
