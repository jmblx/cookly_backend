from typing import Sequence

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from application.resource_server.common.rs_repo import ResourceServerRepository
from application.resource_server.dtos import ResourceServerCreateDTO
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerID


class ResourceServerRepositoryImpl(ResourceServerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, rs_id: ResourceServerID
    ) -> ResourceServer | None:
        rs = await self.session.get(ResourceServer, rs_id)
        return rs

    async def get_many_by_ids(
        self, rs_ids: list[ResourceServerID]
    ) -> Sequence[ResourceServer]:
        if not rs_ids:
            return []

        result = await self.session.execute(
            select(ResourceServer).where(ResourceServer.id.in_(rs_ids))
        )
        return result.scalars().all()

    async def save(
        self, resource_server: ResourceServer
    ) -> ResourceServerCreateDTO:
        resource_server = await self.session.merge(resource_server)
        await self.session.flush()
        return ResourceServerCreateDTO(resource_server.id)
