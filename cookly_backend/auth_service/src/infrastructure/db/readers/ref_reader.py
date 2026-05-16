import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.client.client_ref.common.reader import RefReader
from application.common.views.rs_view import ResourceServerIdsData
from domain.entities.client.model import Client
from domain.entities.client.ref_model import ClientRef
from presentation.web_api.routes.client.refs.models import RefView


class RefReaderImpl(RefReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_ref_page_view(
        self, ref_id: int
    ) -> RefView | None:
        stmt = (
            select(ClientRef)
            .where(ClientRef.id == ref_id)
            .options(
                selectinload(ClientRef.resource_servers),
            )
        )
        ref: ClientRef = await self.session.scalar(stmt)
        client = await self.session.get(Client, ref.client_id)
        return RefView(
            name=ref.name, user_scopes=ref.user_scopes.value, client_name=client.name.value, ref_resource_servers={
                rs.id: ResourceServerIdsData(rs.name) for rs in ref.resource_servers
            }
        )
