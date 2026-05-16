from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dishka import Provider, Scope, provide
from fastapi import Request

from application.common.types import AccessToken


def from_user_tz(dt: datetime, tz):
    return dt.replace(tzinfo=tz).astimezone(ZoneInfo("UTC"))


class PresentationProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=AccessToken)
    def provide_access_token(self, request: Request) -> AccessToken:
        headers = {
            key.lower(): value for key, value in request.headers.items()
        }
        auth_header = headers.get("authorization")
        if auth_header:
            return AccessToken(auth_header.replace("Bearer ", ""))

    @provide(scope=Scope.REQUEST, provides=ZoneInfo)
    def provide_timezone(self, request: Request) -> ZoneInfo:
        headers = {
            key.lower(): value for key, value in request.headers.items()
        }

        tz_name = headers.get("x-timezone", "UTC")

        try:
            return ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            return ZoneInfo("UTC")
