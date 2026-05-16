from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import composite, relationship

from domain.entities.client.ref_model import ClientRef
from domain.entities.client.value_objects import UserScopes
from infrastructure.db.models.registry import mapper_registry
from infrastructure.db.models.secondary import client_ref_rs_association_table

client_ref_table = Table(
    "client_ref",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("user_scopes", ARRAY(String), nullable=False),
    Column("client_id", Integer, ForeignKey("client.id"), nullable=False),
)


mapper_registry.map_imperatively(
    ClientRef,
    client_ref_table,
    properties={
        "id": client_ref_table.c.id,
        "name": client_ref_table.c.name,
        "user_scopes": composite(UserScopes, client_ref_table.c.user_scopes),
        "client_id": client_ref_table.c.client_id,
        "client": relationship(
            "Client", back_populates="refs", uselist=False
        ),
        "resource_servers": relationship(
            "ResourceServer",
            uselist=True,
            back_populates="client_refs",
            secondary=client_ref_rs_association_table,
        ),
    },
    column_prefix="_",
)
