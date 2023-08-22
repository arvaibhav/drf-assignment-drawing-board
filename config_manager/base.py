import os


class JwtConfig:
    def __init__(
        self, secret_key, refresh_secret_key, expire_in_sec, refresh_expire_in_sec
    ):
        self.SECRET_KEY = secret_key
        self.REFRESH_SECRET_KEY = refresh_secret_key
        self.EXPIRE_IN_SEC = expire_in_sec
        self.REFRESH_EXPIRE_IN_SEC = refresh_expire_in_sec


class BaseConfig:
    JWT_CONFIG = JwtConfig(
        secret_key=os.environ.get(
            "JWT_SECRET_KEY",
            "8cf4407cbe0e24f00e30f2cdddcd97b106d90fd0a37312fb3e440b64194b7de5",
        ),
        refresh_secret_key=os.environ.get(
            "JWT_REFRESH_SECRET_KEY",
            "8cf4407cbe0e24f00e30f2cdddcd97b106d90fd0a37312fb3e440b64194b7de5",
        ),
        expire_in_sec=int(os.environ.get("EXPIRE_IN_SEC", 300)),
        refresh_expire_in_sec=int(os.environ.get("REFRESH_EXPIRE_IN_SEC", 3600)),
    )
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
