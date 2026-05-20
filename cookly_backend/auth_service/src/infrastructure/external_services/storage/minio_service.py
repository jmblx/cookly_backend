import os
import time
from datetime import timedelta
from io import BytesIO

import PIL
from minio import Minio
from minio.error import S3Error
from PIL import Image
from redis.asyncio import Redis

from application.common.interfaces.imedia_storage import (
    SetAvatarResponse,
    StorageService,
    UserS3StorageService,
)
from infrastructure.external_services.storage.config import MinIOConfig
from infrastructure.external_services.storage.exceptions import InvalidImageError


class MinIOService(StorageService):
    def __init__(self, config: MinIOConfig, bucket_name: str):
        self.config = config
        self.s3_client = Minio(
            config.endpoint_url,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )
        self.bucket_name = bucket_name

    def _process_avatar(self, content: bytes) -> bytes:
        """
        Обрезает и конвертирует изображение в webp.
        """
        try:
            with Image.open(BytesIO(content)) as img:
                img = img.convert("RGB")
                img = img.resize((256, 256), Image.LANCZOS)
                output = BytesIO()
                img.save(output, format="WEBP", quality=90)
                return output.getvalue()
        except PIL.UnidentifiedImageError:
            raise InvalidImageError

    def _get_avatar_filename(self, object_id: str) -> str:
        return f"{object_id}.webp"

    async def set_avatar(
        self, content: bytes, content_type: str, object_id: str
    ) -> SetAvatarResponse:
        """
        Загружает аватарку в MinIO.
        """
        filename = f"{object_id}.webp"
        try:
            processed_content = self._process_avatar(content)
            self.s3_client.put_object(
                self.bucket_name,
                filename,
                BytesIO(processed_content),
                length=len(processed_content),
                content_type="image/webp",
            )
            return {
                "avatar_presigned_url": self.get_presigned_avatar_url(
                    object_id
                )
            }
        except S3Error as e:
            raise Exception(f"Ошибка при загрузке файла в MinIO: {e}")

    def get_presigned_avatar_url(self, object_id: str) -> str:
        """
        Генерирует presigned URL для доступа к аватарке.
        Заменяет хост в URL на public_url.
        """
        try:
            presigned_url = self.s3_client.presigned_get_object(
                self.bucket_name,
                self._get_avatar_filename(object_id),
                expires=timedelta(minutes=5),
            )
            presigned_url = presigned_url.replace(
                "http://minio:9000", os.getenv("HOST_ADDRESS")
            )

            return presigned_url
        except S3Error as e:
            raise Exception(f"Ошибка при генерации presigned URL: {e}")


class UserMinIOService(UserS3StorageService, MinIOService):
    def __init__(self, config: MinIOConfig, bucket_name: str, redis: Redis):
        super().__init__(config, bucket_name)
        self.redis = redis

    async def set_avatar(
        self, content: bytes, content_type: str, object_id: str
    ) -> SetAvatarResponse:
        """
        Загружает аватарку в MinIO и сохраняет время загрузки в Redis.
        """
        new_avatar_data = await super().set_avatar(
            content, content_type, object_id
        )
        avatar_update_timestamp = int(time.time())
        await self.redis.set(
            f"user_avatar:{object_id}", avatar_update_timestamp
        )
        new_avatar_data["avatar_update_timestamp"] = avatar_update_timestamp
        return new_avatar_data

    async def get_user_avatar_update_timestamp(
        self, user_id: str
    ) -> int | None:
        value = await self.redis.get(f"user_avatar:{user_id}")
        return int(value) if value else None
