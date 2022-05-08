from abc import ABC, abstractmethod

from .logger import log


class ADT(ABC):
    def to_dict(self, ctx):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, obj, ctx):
        if obj is None:
            return None
        return cls(**obj)
    
    @classmethod
    @property
    @abstractmethod
    def schema(cls) -> str:
        pass
    
    @staticmethod
    def delivery_callback(err: str, msg: str) -> None:
        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently
        # failed delivery (after retries).
        if err:
            log.error("Message failed delivery: {}".format(err))
        else:
            log.debug(
                "Produced event to {topic}: key={key:12}".format(
                    topic=msg.topic(),
                    key=int.from_bytes(msg.key(), "big"),
                )
            )
