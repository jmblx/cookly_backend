from io import BytesIO

import PIL
from minio import Minio, S3Error
from PIL import Image

from application.common.errors.exceptions import InfrastructureError
from application.common.interfaces.s3_storage import S3Storage
from application.recipe.common.exceptions import InvalidImageError
from core.config import MinioConfig


class MinioService(S3Storage):
    def __init__(self, config: MinioConfig):
        self.config = config
        self.s3_client = Minio(
            config.endpoint_url,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )

    def _process_image(self, content: bytes) -> bytes:
        """
        Обрезает и конвертирует изображение в webp.
        """
        try:
            with Image.open(BytesIO(content)) as img:
                # img = img.convert("RGB")
                # img = img.resize((256, 256), Image.LANCZOS)
                output = BytesIO()
                img.save(output, format="WEBP", quality=90)
                return output.getvalue()
        except PIL.UnidentifiedImageError as e:
            raise InvalidImageError from e

    def _get_avatar_filename(self, object_id: str) -> str:
        return f"{object_id}.webp"

    async def _set_image(
        self, content: bytes, object_id: str, bucket_name: str
    ) -> str:
        filename = f"{object_id}.webp"
        try:
            processed_content = self._process_image(content)
            self.s3_client.put_object(
                bucket_name,
                filename,
                BytesIO(processed_content),
                length=len(processed_content),
                content_type="image/webp",
            )
        except S3Error as err:
            raise InfrastructureError from err
        else:
            return f"{self.config.url}/{bucket_name}/{filename}"

    async def set_recipe_image(self, content: bytes, object_id: str) -> str:
        return await self._set_image(content, object_id, self.config.recipe_bucket_name)

    async def set_recipe_step_image(self, content: bytes, object_id: str) -> str:
        return await self._set_image(content, object_id, self.config.recipe_step_bucket_name)
