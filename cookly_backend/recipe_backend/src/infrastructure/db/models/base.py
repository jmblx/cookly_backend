from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, registry

from infrastructure.db.models.common import intpk

mapper_registry = registry(metadata=MetaData())


class Base(DeclarativeBase):
    registry = mapper_registry
    metadata = mapper_registry.metadata

    id: Mapped[intpk]

    __abstract__ = True
