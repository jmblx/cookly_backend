from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

from presentation.web_api.tz_context import current_tz


class BaseTZModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def convert_datetime_to_utc(cls, value):
        if isinstance(value, datetime):
            tz = current_tz.get()

            if value.tzinfo is None:
                value = value.replace(tzinfo=tz)

            return value.astimezone(ZoneInfo("UTC"))

        return value
