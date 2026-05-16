import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.orm import relationship

from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerType
from infrastructure.db.models.registry import mapper_registry
from infrastructure.db.models.secondary import user_rs_association_table, client_ref_rs_association_table

rs_table = sa.Table(
    "resource_server",
    mapper_registry.metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("name", sa.String, nullable=False),
    sa.Column(
        "type",
        sa.Enum(ResourceServerType, name="access_control_type_enum"),
        nullable=False,
    ),
    sa.Column("search_name", sa.String, nullable=False),
    Index(
        "idx_resource_server_search_name_trgm",
        "search_name",
        postgresql_using="gin",
        postgresql_ops={"search_name": "gin_trgm_ops"},
    ),
)

mapper_registry.map_imperatively(
    ResourceServer,
    rs_table,
    properties={
        "id": rs_table.c.id,
        "name": rs_table.c.name,
        "type": rs_table.c.type,
        "search_name": rs_table.c.search_name,
        # "clients": relationship("Client", secondary=client_rs_association_table, back_populates="resource_servers", uselist=True),
        "roles": relationship(
            "Role", back_populates="resource_server", uselist=True
        ),
        "users_rss": relationship(
            "User",
            back_populates="resource_servers",
            uselist=True,
            secondary=user_rs_association_table,
        ),
        "client_refs": relationship(
            "ClientRef",
            uselist=True,
            back_populates="resource_servers",
            secondary=client_ref_rs_association_table,
        ),
    },
    column_prefix="_",
)
