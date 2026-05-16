import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.di.container import container
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerID


async def test(rs_ids: list[ResourceServerID]):
    sessionmaker = await container.get(async_sessionmaker[AsyncSession])  # await корутину
    async with sessionmaker() as s:                     # теперь норм
        result = await s.execute(
            select(ResourceServer).where(ResourceServer.id.in_(rs_ids))
        )
        rss = result.scalars().all()
        print("ddd")
        print(rss)



asyncio.run(test([1, 2]))