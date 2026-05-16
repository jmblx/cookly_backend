from abc import ABC, abstractmethod

from domain.entities.role.model import Role
from domain.entities.role.value_objects import RoleID


class RoleReader(ABC):
    @abstractmethod
    async def by_id(self, role_id: RoleID) -> Role | None:
        """Получить пользователя по ID."""
        raise NotImplementedError
