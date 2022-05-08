import struct

from confluent_kafka.serialization import (
    Deserializer,
    SerializationError,
    Serializer,
)


class LongSerializer(Serializer):
    def __call__(self, obj, ctx):
        if obj is None:
            return None
        try:
            return struct.pack(">Q", obj)
        except struct.error as e:
            raise SerializationError(str(e))


class LongDeserializer(Deserializer):
    def __call__(self, value, ctx):
        if value is None:
            return None
        try:
            return struct.unpack(">Q", value)[0]
        except struct.error as e:
            raise SerializationError(str(e))
