import typing

from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.role_repo import RoleRepository
from application.common.views.role_view import RoleViewWithId
from application.common.views.rs_view import (
    ResourceServerIdsData,
    ResourceServerView,
)
from application.resource_server.common.rs_reader import (
    ResourceServerData,
    ResourceServerReader,
)
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import (
    ResourceServerID,
    ResourceServerType,
)
from domain.exceptions.resource_server import ResourceServerNotFoundError
from infrastructure.db.models import rs_table
from infrastructure.db.readers.common import change_layout


class ResourceServerReaderImpl(ResourceServerReader):
    def __init__(self, session: AsyncSession, role_repository: RoleRepository):
        self.session = session
        self.role_repo = role_repository

    async def get_resource_server_data_by_ids(
        self, rs_ids: list[ResourceServerID]
    ) -> dict[ResourceServerID, ResourceServerData]:
        query = select(ResourceServer.id, ResourceServer.name).where(
            rs_table.c.id.in_(rs_ids)
        )
        resource_servers = await self.session.execute(query)
        return {rs.id: {"name": rs.name} for rs in resource_servers}

    async def read_for_rs_page(
        self, rs_id: ResourceServerID
    ) -> ResourceServerView | None:
        resource_server = await self.session.get(ResourceServer, rs_id)
        if not resource_server:
            raise ResourceServerNotFoundError()
        resource_server_data: ResourceServerView = {
            "name": resource_server.name,
            "type": resource_server.type,
        }
        if resource_server.type == ResourceServerType.RBAC_BY_AS:
            resource_server_roles = await self.role_repo.get_roles_by_rs_id(
                rs_id, order_by_id=True
            )
            if resource_server_roles:
                resource_server_data["roles"] = [
                    typing.cast(
                        RoleViewWithId,
                        {
                            "id": role.id,
                            "name": role.name.value,
                            "base_scopes": role.base_scopes.to_list(),
                            "is_base": role.is_base,
                        },
                    )
                    for role in resource_server_roles
                ]
        return resource_server_data

    async def read_all_resource_server_ids_data(
        self, from_: int, limit: int
    ) -> dict[ResourceServerID, ResourceServerIdsData]:
        query = (
            select(ResourceServer.id, ResourceServer.name)
            .where(ResourceServer.id > from_)
            .limit(limit)
        )
        data = await self.session.execute(query)
        resource_servers_data = data.mappings().all()
        result = {
            resource_server["id"]: ResourceServerIdsData(
                name=resource_server["name"]
            )
            for resource_server in resource_servers_data
        }
        return result

    async def find_by_marks(
        self, search_input: str, similarity: float = 0.3
    ) -> dict[ResourceServerID, ResourceServerIdsData] | None:
        await self.session.execute(
            text(f"SET LOCAL pg_trgm.similarity_threshold = {similarity};")
        )
        marks_converted = change_layout(search_input)
        query = select(ResourceServer.id, ResourceServer.name).where(
            or_(
                rs_table.c.search_name.op("%")(search_input),
                rs_table.c.search_name.op("%")(marks_converted),
            )
        )
        rss_data = (await self.session.execute(query)).mappings().all()
        result = {
            rs["id"]: ResourceServerIdsData(name=rs["name"]) for rs in rss_data
        }
        return result
