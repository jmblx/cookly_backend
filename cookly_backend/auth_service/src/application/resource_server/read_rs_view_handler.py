from dataclasses import dataclass

from application.common.views.rs_view import ResourceServerView
from application.resource_server.common.rs_reader import ResourceServerReader
from domain.entities.resource_server.value_objects import ResourceServerID


@dataclass
class ReadResourceServerPageViewQuery:
    rs_id: int


class ReadResourceServerPageViewQueryHandler:
    def __init__(self, rs_reader: ResourceServerReader):
        self.rs_reader = rs_reader

    async def handle(
        self, query: ReadResourceServerPageViewQuery
    ) -> ResourceServerView:
        rs_view = await self.rs_reader.read_for_rs_page(
            ResourceServerID(query.rs_id)
        )
        return rs_view
