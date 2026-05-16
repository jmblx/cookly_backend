import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(r"D:\vs\RKSI2024\auth-service\.env")

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DATABASE_URI = os.environ.get(
    "DATABASE_URI",
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)
print(DATABASE_URI)


@dataclass(frozen=True)
class DatabaseConfig:
    db_uri: str

    @staticmethod
    def from_env() -> "DatabaseConfig":
        uri = os.getenv("DATABASE_URI", DATABASE_URI)

        if not uri:
            raise RuntimeError("Missing DATABASE_URI environment variable")

        return DatabaseConfig(uri)
