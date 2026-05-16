import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

endpoint_url = os.getenv("MINIO_ENDPOINT_URL")
try:
    import aiobotocore

    endpoint_url: str = (
        endpoint_url
        if endpoint_url.startswith(("http://", "https://"))
        else f"http://{endpoint_url}"
    )
except ModuleNotFoundError:
    pass


class MinIOConfig(BaseModel):
    endpoint_url: str = endpoint_url
    access_key: str = os.getenv("MINIO_ACCESS_KEY")
    secret_key: str = os.getenv("MINIO_SECRET_KEY")
    public_url: str = os.getenv("MINIO_PUBLIC_URL")
