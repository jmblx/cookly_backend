from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypedDict

from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email, UserID


class IdentificationFields(TypedDict, total=False):
    id: UserID | None
    email: Email | None


class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None:
        """Сохранить пользователя в базе данных."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: User) -> None:
        """Удалить пользователя по ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_fields_with_clients(
        self, fields: IdentificationFields
    ) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, user_id: UserID) -> User | None:
        """Получить пользователя по ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Получить пользователя по email."""
        raise NotImplementedError

    @abstractmethod
    async def add_roles_to_user(
        self, user_id: UserID, role_ids: list[int]
    ) -> None: ...

    @abstractmethod
    async def add_rs_to_user(
        self, user_id: UserID, rs_ids: Sequence[ResourceServerID]
    ) -> None: ...
