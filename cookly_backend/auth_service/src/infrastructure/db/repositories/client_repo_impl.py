from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.client.common.client_repo import ClientRepository
from application.dtos.client import ClientCreateDTO
from domain.entities.client.model import Client
from domain.entities.client.value_objects import ClientID
from infrastructure.db.models.client_models import client_table


class ClientRepositoryImpl(ClientRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, client: Client) -> ClientCreateDTO:
        """
        Сохраняет объект клиента (Client) в базе данных.
        """
        client = await self.session.merge(client)
        await self.session.flush()
        return ClientCreateDTO(client_id=client.id)

    async def get_by_id(self, client_id: ClientID) -> Client | None:
        return await self.session.get(Client, client_id)

    async def delete(self, client_id: ClientID) -> None:
        """
        Удаляет клиента по его идентификатору.
        """
        query = select(client_table).where(
            and_(client_table.c.id == client_id)
        )
        result = await self.session.execute(query)
        client = result.scalar_one_or_none()
        if client:
            await self.session.delete(client)
