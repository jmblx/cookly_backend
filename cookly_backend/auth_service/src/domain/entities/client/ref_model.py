from dataclasses import dataclass, field
from typing import Sequence

from domain.common.logic_types import UserScope
from domain.entities.client.value_objects import UserScopes, ClientID
from domain.entities.resource_server.model import ResourceServer


@dataclass
class ClientRef:
    id: int = field(init=False)
    name: str
    user_scopes: UserScopes
    client_id: ClientID
    resource_servers: list[ResourceServer] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        user_scopes: list[UserScope],
        client_id: int,
        resource_servers: Sequence[ResourceServer] | None = None,
    ) -> "ClientRef":
        return cls(
            name=name,
            user_scopes=UserScopes(user_scopes),
            client_id=ClientID(client_id),
            resource_servers=resource_servers if resource_servers is not None else [],
        )
