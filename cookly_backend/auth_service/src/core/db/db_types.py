import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, text  # , ForeignKey
from sqlalchemy.orm import mapped_column

# Базовые аннотации для моделей БД
added_at = Annotated[
    datetime.datetime,
    mapped_column(
        nullable=True, server_default=text("TIMEZONE('utc', now())")
    ),
]
updated_at = added_at

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

# intfk = Annotated[int, mapped_column(ForeignKey(
#   "match.id", primary_key=True)
# )]
achievement_fk = Annotated[
    int, mapped_column(ForeignKey("achievement.id"), nullable=True)
]
event_fk = Annotated[int, mapped_column(ForeignKey("event.id"), nullable=True)]
reward_fk = Annotated[
    int, mapped_column(ForeignKey("reward.id"), nullable=True)
]
purchase_fk = Annotated[
    int, mapped_column(ForeignKey("purchase.id"), nullable=True)
]
user_fk = Annotated[str, mapped_column(ForeignKey("user.id"), nullable=True)]
not_null_user_fk = Annotated[
    str, mapped_column(ForeignKey("user.id"), nullable=False)
]
