import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.third_party_auth.common.idp import (
    OAuth2Token,
    OauthIdentityProvider,
)
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email


class YandexIdentityProvider(OauthIdentityProvider):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_yandex_user_email(self, oauth_token: str) -> Email:
        if not oauth_token:
            raise ValueError("Токен не может быть пустым")

        headers = {"Authorization": f"OAuth {oauth_token}"}
        url = "https://login.yandex.ru/info?format=json"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return Email(data.get("default_email"))

        except aiohttp.ClientResponseError as e:
            raise ValueError(
                f"Ошибка запроса к Яндекс ID: {e.status} - {e.message}"
            )
        except aiohttp.ClientError as e:
            raise ValueError(f"Сетевая ошибка: {e!s}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Ошибка обработки ответа: {e!s}")

    async def get_current_user(self, oauth_token: OAuth2Token) -> User:
        email = await self.get_yandex_user_email(oauth_token)
        query = select(User).where(User.email == email)
        user = (await self.session.execute(query)).scalar()
        return user
