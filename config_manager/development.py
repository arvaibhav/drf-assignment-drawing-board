import os
from config_manager import BaseConfig
from config_manager.base import JwtConfig


class DevelopmentConfig(BaseConfig):
    JWT_CONFIG = JwtConfig(
        secret_key=os.environ.get(
            "JWT_SECRET_KEY",
            "8cf4407cbe0e24f00e30f2cdddcd97b106d90fd0a37312fb3e440b64194b7de5",
        ),
        refresh_secret_key=os.environ.get(
            "JWT_REFRESH_SECRET_KEY",
            "8cf4407cbe0e24f00e30f2cdddcd97b106d90fd0a37312fb3e440b64194b7de5",
        ),
        expire_in_sec=3600,
        refresh_expire_in_sec=3600,
    )
