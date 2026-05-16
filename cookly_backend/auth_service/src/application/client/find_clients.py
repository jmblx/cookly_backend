from dataclasses import dataclass

from application.client.common.client_reader import ClientReader
from application.common.views.client_view import ClientsIdsData
from domain.entities.client.value_objects import ClientID


@dataclass
class FindClientsQuery:
    search_input: str


class FindClientsHandler:
    def __init__(self, client_reader: ClientReader):
        self.client_reader = client_reader

    async def handle(
        self, query: FindClientsQuery
    ) -> dict[ClientID, ClientsIdsData]:
        return await self.client_reader.find_by_marks(
            query.search_input.strip().lower()
        )
