from contextvars import ContextVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

current_tz: ContextVar[ZoneInfo] = ContextVar("current_tz", default=ZoneInfo("Europe/Moscow"))


class TimezoneMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tz_name = request.headers.get("X-Timezone", "Europe/Moscow")

        try:
            tz = ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo("Europe/Moscow")

        token = current_tz.set(tz)

        try:
            response = await call_next(request)
        finally:
            current_tz.reset(token)

        return response
