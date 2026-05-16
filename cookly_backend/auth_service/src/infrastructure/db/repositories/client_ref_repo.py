import sqlalchemy.dialects.postgresql as sa_pg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.client.client_ref.common.repo import SaveRefDTO, RefRepository
from domain.entities.client.ref_model import ClientRef
from infrastructure.db.models.secondary import client_ref_rs_association_table


class RefRepositoryImpl(RefRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, ref: ClientRef) -> SaveRefDTO:
        persistent = None
        if ref.id is not None:
            stmt = (
                select(ClientRef)
                .where(ClientRef.id == ref.id)
                .options(selectinload(ClientRef.resource_servers))
            )
            persistent = (await self.session.execute(stmt)).scalar_one()

        if persistent:
            persistent.name = ref.name
            persistent.user_scopes = ref.user_scopes
            persistent.resource_servers = ref.resource_servers
            ref = persistent
        else:
            ref = await self.session.merge(ref)

        await self.session.flush()
        return SaveRefDTO(ref_id=ref.id)

    async def get_by_id(self, ref_id: int) -> ClientRef | None:
        stmt = (
            select(ClientRef)
            .where(ClientRef.id == ref_id)
            .options(selectinload(ClientRef.resource_servers))
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()