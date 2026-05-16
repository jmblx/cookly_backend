import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.db.models.registry import mapper_registry

# Association Table between User and Client
user_client_association_table = Table(
    "user_client_association",
    mapper_registry.metadata,
    Column("id", sa.Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    ),
    Column("client_id", sa.Integer, ForeignKey("client.id"), nullable=False),
)

user_role_association = Table(
    "user_role_association",
    mapper_registry.metadata,
    Column("id", sa.Integer, primary_key=True, autoincrement=True),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    ),
    Column("role_id", sa.Integer, ForeignKey("role.id"), nullable=False),
)

client_rs_association_table = Table(
    "client_rs_association_table",
    mapper_registry.metadata,
    Column("id", sa.Integer, primary_key=True, autoincrement=True),
    Column("client_id", sa.Integer, ForeignKey("client.id"), nullable=False),
    Column(
        "rs_id", sa.Integer, ForeignKey("resource_server.id"), nullable=False
    ),
)

user_rs_association_table = Table(
    "user_rs_association_table",
    mapper_registry.metadata,
    Column("id", sa.Integer, primary_key=True, autoincrement=True),
    Column(
        "rs_id", sa.Integer, ForeignKey("resource_server.id"), nullable=False
    ),
    Column(
        "user_id", PGUUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    ),
)

client_ref_rs_association_table = Table(
    "client_ref_rs_association_table",
    mapper_registry.metadata,
    Column("id", sa.Integer, primary_key=True, autoincrement=True),
    Column("client_ref_id", sa.Integer, ForeignKey("client_ref.id"), nullable=False),
    Column("rs_id", sa.Integer, ForeignKey("resource_server.id"), nullable=False),
)
