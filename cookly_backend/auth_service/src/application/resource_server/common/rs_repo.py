from abc import abstractmethod
from typing import Sequence

from application.resource_server.dtos import ResourceServerCreateDTO
from domain.entities.resource_server.model import ResourceServer
from domain.entities.resource_server.value_objects import ResourceServerID


@abstractmethod
class ResourceServerRepository:
    @abstractmethod
    async def get_by_id(
        self, rs_id: ResourceServerID
    ) -> ResourceServer | None: ...

    @abstractmethod
    async def save(
        self, resource_server: ResourceServer
    ) -> ResourceServerCreateDTO: ...

    @abstractmethod
    async def get_many_by_ids(
        self, rs_ids: list[ResourceServerID]
    ) -> Sequence[ResourceServer]: ...
