from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

from core.db.db_types import added_at
from infrastructure.db.models.registry import mapper_registry

BaseDec = declarative_base(metadata=mapper_registry.metadata)


class Base(BaseDec):
    __abstract__ = True

    created_at: Mapped[added_at]
    updated_at: Mapped[added_at]
    is_active: Mapped[bool] = mapped_column(nullable=True)
