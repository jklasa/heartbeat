import json
from configparser import ConfigParser
from typing import Callable

from common.adt import ADT
from common.long_serialization import LongDeserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer


class Consumer(DeserializingConsumer):
    def __init__(
        self,
        config_file: str,
        schema_file: str,
        registry_file: str,
        data: ADT,
        *args,
        **kwargs
    ):
        # Parse the configuration.
        # https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
        config_parser = ConfigParser()
        with open(config_file) as file:
            config_parser.read_file(file)
        config = dict(config_parser["default"]) | dict(
            config_parser["consumer"]
        )

        # Create Consumer instance
        with open(registry_file) as f:
            schema_registry_conf = json.load(f)
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        avro_deserializer = AvroDeserializer(
            schema_registry_client, data.schema, data.from_dict
        )
        config |= {
            "key.deserializer": LongDeserializer(),
            "value.deserializer": avro_deserializer,
        }
        
        super().__init__(config, *args, **kwargs)
