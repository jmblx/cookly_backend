from abc import ABC, abstractmethod

from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.role.model import Role


class ScopesService(ABC):
    @abstractmethod
    def calculate_full_user_scopes_for_client(
        self, roles_by_rs: dict[ResourceServerID, list[Role] | list[dict]]
    ) -> list[str]: ...
