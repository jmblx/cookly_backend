import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")


@dataclass(frozen=True)
class RedisConfig:
    rd_uri: str

    @staticmethod
    def from_env() -> "RedisConfig":
        uri = os.environ.get("REDIS_URI", f"redis://{REDIS_HOST}:{REDIS_PORT}")

        if not uri:
            raise RuntimeError("Missing REDIS_URI environment variable")

        return RedisConfig(uri)
