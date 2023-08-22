import os
from typing import Type

from dotenv import load_dotenv

load_dotenv()
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig


def get_config() -> Type[BaseConfig]:
    if BaseConfig.DEBUG:
        return DevelopmentConfig
    else:
        return ProductionConfig
