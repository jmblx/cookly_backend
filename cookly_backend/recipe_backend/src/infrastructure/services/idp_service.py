import aiohttp
from starlette import status

from application.common.interfaces.idp_service import IDPService
from application.common.types import AccessToken
from core.config import AuthCoreConfig, MinioConfig


class AuthCoreIDPService(IDPService):
    def __init__(
        self,
        config: AuthCoreConfig,
        access_token: AccessToken,
        http_session: aiohttp.ClientSession,
        minio_config: MinioConfig
    ):
        self.config = config
        self.access_token = access_token
        self.http_session = http_session
        self.minio_config = minio_config

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    async def get_user_data(self):
        api_url = self.config.api_url
        me_endpoint = api_url + "/userinfo"
        async with self.http_session.get(me_endpoint, headers=self._get_headers()) as response:
            if response.status == status.HTTP_200_OK:
                data = await response.json()
                data["user_avatar"] = (
                    f"{self.minio_config.url}/{self.minio_config.user_avatar_bucket_name}/{data['id']}.webp"
                )
        return data
