from sqlalchemy import (
    UUID as SQLAlchemyUUID,
)
from sqlalchemy import (
    Boolean,
    Column,
    String,
    Table,
)
from sqlalchemy.orm import composite, relationship

from domain.entities.user.model import User
from domain.entities.user.value_objects import Email, HashedPassword, UserID
from infrastructure.db.models.registry import mapper_registry
from infrastructure.db.models.secondary import (
    user_role_association,
    user_rs_association_table,
)

user_table = Table(
    "user",
    mapper_registry.metadata,
    Column("id", SQLAlchemyUUID(as_uuid=True), primary_key=True),
    Column("email", String, nullable=False),
    Column("is_email_confirmed", Boolean, default=False),
    Column("hashed_password", String, nullable=False),
    Column("is_admin", Boolean, nullable=False),
)

mapper_registry.map_imperatively(
    User,
    user_table,
    properties={
        "id": composite(UserID, user_table.c.id),
        "email": composite(Email, user_table.c.email),
        "hashed_password": composite(
            HashedPassword, user_table.c.hashed_password
        ),
        "is_email_confirmed": user_table.c.is_email_confirmed,
        "roles": relationship(
            "Role",
            secondary=user_role_association,
            back_populates="users_roles",
            uselist=True,
        ),
        "resource_servers": relationship(
            "ResourceServer",
            uselist=True,
            back_populates="users_rss",
            secondary=user_rs_association_table,
        ),
        "is_admin": user_table.c.is_admin,
        # "clients": relationship(
        #     "Client",
        #     secondary=user_client_association_table,
        #     back_populates="users",
        #     uselist=True,
        # ),
    },
    column_prefix="_",
)
