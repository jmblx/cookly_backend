import datetime
from typing import Annotated

from sqlalchemy import DateTime, text
from sqlalchemy.orm import mapped_column

added_at = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    ),
]
datetime_tz = Annotated[
    datetime.datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=True,
    ),
]
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
