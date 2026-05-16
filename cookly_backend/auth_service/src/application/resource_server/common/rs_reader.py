from abc import ABC, abstractmethod
from typing import TypedDict

from application.common.views.rs_view import (
    ResourceServerIdsData,
    ResourceServerView,
)
from domain.entities.resource_server.value_objects import ResourceServerID


class ResourceServerData(TypedDict):
    name: str


class ResourceServerReader(ABC):
    @abstractmethod
    async def get_resource_server_data_by_ids(
        self, rs_ids: list[ResourceServerID]
    ) -> dict[ResourceServerID, ResourceServerData]: ...

    @abstractmethod
    async def read_for_rs_page(
        self, rs_id: ResourceServerID
    ) -> ResourceServerView | None: ...

    @abstractmethod
    async def read_all_resource_server_ids_data(
        self, from_: int, limit: int
    ) -> dict[ResourceServerID, ResourceServerIdsData]: ...

    @abstractmethod
    async def find_by_marks(
        self, search_input: str, similarity: float = 0.3
    ) -> dict[ResourceServerID, ResourceServerIdsData] | None: ...
