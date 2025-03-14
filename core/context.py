
import os
from dotenv import load_dotenv
from core.singleton_meta import SingletonMeta
from fastapi import FastAPI


class Context(metaclass=SingletonMeta):
    _app: FastAPI
    _data: dict = {}

    @classmethod
    def init(cls, app: FastAPI):
        cls._app = app
        cls._init_env()

    @classmethod
    def clear(cls):
        cls._data.clear()

    @classmethod
    def get(cls, key: str, default=None):
        return cls._data.get(key, default)

    @classmethod
    def set(cls, key: str, value):
        cls._data[key] = value
        
    @classmethod
    def _init_env(cls):
        load_dotenv()
        cls._data['_env'] = {key: value for key, value in os.environ.items()}
        
    @classmethod
    def get_envs(cls) -> dict:
        return cls._data['_env']
