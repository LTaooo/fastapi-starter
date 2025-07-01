from abc import ABC


class BaseProducer(ABC):
    @classmethod
    def get_routing_key(cls) -> str:
        raise NotImplementedError
