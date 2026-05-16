from datetime import datetime
from typing import NewType, TypedDict
from uuid import UUID

SessionHash = NewType("SessionHash", str)
AccessToken = NewType("AccessToken", str)


class AccessTokenPayload(TypedDict, total=False):
    sub: UUID
    exp: datetime
    iat: datetime
    jti: UUID
    scopes: list[str]


Timezone = NewType("Timezone", str)
