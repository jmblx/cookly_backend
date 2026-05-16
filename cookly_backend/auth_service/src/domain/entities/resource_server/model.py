from dataclasses import dataclass, field
from typing import Self

from domain.entities.resource_server.value_objects import (
    ResourceServerID,
    ResourceServerType,
)


@dataclass
class ResourceServer:
    id: ResourceServerID = field(init=False)
    name: str
    type: ResourceServerType
    search_name: str

    @classmethod
    def create(
        cls,
        name: str,
        type: ResourceServerType,
    ) -> Self:
        resource_server = cls(
            name,
            type,
            search_name=name.strip().lower(),
        )
        return resource_server

    def rename(self, name: str) -> None:
        self.name = name
        self.search_name = name.strip().lower()
