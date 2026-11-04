import os
from pathlib import Path

from dotenv import dotenv_values

BASE_ENV_FILE = Path('.env')
DEFAULT_APP_ENV = 'dev'


def _get_app_env() -> str:
    app_env = os.getenv('APP_ENV')
    if not app_env and BASE_ENV_FILE.exists():
        app_env = dotenv_values(BASE_ENV_FILE).get('APP_ENV')
    value = str(app_env or DEFAULT_APP_ENV).strip()
    return value.strip('"\'').lower()


APP_ENV = _get_app_env()
ENV_FILES = (str(BASE_ENV_FILE), f'{BASE_ENV_FILE}.{APP_ENV}')
