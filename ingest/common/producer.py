import json
from configparser import ConfigParser
from typing import Callable, Optional

from common.adt import ADT
from common.long_serialization import LongSerializer
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


class Producer(SerializingProducer):
    def __init__(
        self,
        topic: str,
        config_file: str,
        registry_file: str,
        data: ADT,
        do_callback: bool = True,
        *args,
        **kwargs,
    ):
        self.topic = topic
        self.callback = data.delivery_callback if do_callback else None
        
        # Parse the configuration.
        # https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
        config_parser = ConfigParser()
        with open(config_file) as file:
            config_parser.read_file(file)
        config = dict(config_parser["default"]) | dict(
            config_parser["producer"]
        )

        # Create Producer instance
        with open(registry_file) as f:
            schema_registry_conf = json.load(f)
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)
        avro_serializer = AvroSerializer(
            schema_registry_client, data.schema, data.to_dict
        )
        config |= {
            "key.serializer": LongSerializer(),
            "value.serializer": avro_serializer,
        }

        super().__init__(config, *args, **kwargs)
        
    def produce(self, key, value, *args, **kwargs) -> None:
        super().produce(
            topic=self.topic,
            key=key,
            value=value,
            on_delivery=self.callback,
        )