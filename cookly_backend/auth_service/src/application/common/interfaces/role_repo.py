from abc import ABC, abstractmethod
from collections.abc import Sequence

from domain.entities.client.value_objects import ClientID
from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.role.model import Role
from domain.entities.role.value_objects import RoleID
from domain.entities.user.value_objects import UserID


class RoleRepository(ABC):
    @abstractmethod
    async def save(self, role: Role) -> RoleID: ...

    @abstractmethod
    async def get_by_id(self, role_id: RoleID) -> Role | None: ...

    @abstractmethod
    async def get_roles_by_ids(
        self, role_ids: list[RoleID]
    ) -> Sequence[Role]: ...

    @abstractmethod
    async def get_roles_by_rs_id(
        self, client_id: ResourceServerID, order_by_id: bool = False
    ) -> Sequence[Role]: ...

    @abstractmethod
    async def get_base_rs_roles(self, client_id: ClientID) -> list[Role]: ...

    @abstractmethod
    async def get_user_roles_by_rs_ids(
        self, user_id: UserID, rs_ids: Sequence[ResourceServerID]
    ) -> dict[ResourceServerID, list[Role]]: ...

    @abstractmethod
    async def delete_role(self, role: Role) -> None: ...
