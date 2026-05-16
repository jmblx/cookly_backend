from abc import ABC, abstractmethod
from typing import NewType

from domain.entities.user.model import User

OAuth2Token = NewType("OAuthToken", str)


class OauthIdentityProvider(ABC):
    @abstractmethod
    async def get_yandex_user_email(self, oauth_token: OAuth2Token) -> str: ...

    @abstractmethod
    async def get_current_user(self, oauth_token: OAuth2Token) -> User: ...
