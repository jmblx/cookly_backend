from dataclasses import dataclass

from application.common.views.rs_view import ResourceServerIdsData
from application.resource_server.common.rs_reader import ResourceServerReader
from domain.entities.resource_server.value_objects import ResourceServerID


@dataclass
class FindRSQuery:
    search_input: str


class FindRSHandler:
    def __init__(self, rs_reader: ResourceServerReader):
        self.rs_reader = rs_reader

    async def handle(
        self, query: FindRSQuery
    ) -> dict[ResourceServerID, ResourceServerIdsData]:
        return await self.rs_reader.find_by_marks(
            query.search_input.strip().lower()
        )
