from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite, relationship

from domain.entities.role.model import Role
from domain.entities.role.value_objects import RoleBaseScopes, RoleName
from infrastructure.db.models.registry import mapper_registry
from infrastructure.db.models.secondary import user_role_association

role_table = Table(
    "role",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("base_scopes", JSONB, nullable=False),
    Column("rs_id", Integer, ForeignKey("resource_server.id"), nullable=False),
    Column("is_base", Boolean, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
)


mapper_registry.map_imperatively(
    Role,
    role_table,
    properties={
        "id": role_table.c.id,
        "name": composite(RoleName, role_table.c.name),
        "base_scopes": composite(RoleBaseScopes, role_table.c.base_scopes),
        "users_roles": relationship(
            "User",
            secondary=user_role_association,
            back_populates="roles",
            uselist=True,
        ),
        "rs_id": role_table.c.rs_id,
        "resource_server": relationship(
            "ResourceServer", back_populates="roles", uselist=False
        ),
        "is_base": role_table.c.is_base,
        "is_active": role_table.c.is_active,
    },
    column_prefix="_",
)
