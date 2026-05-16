from abc import ABC, abstractmethod
from typing import TypedDict, Iterable
from uuid import UUID

from domain.entities.user.value_objects import UserID


class UserCardData(TypedDict, total=False):
    email: str


class UserReader(ABC):
    @abstractmethod
    async def get_user_card_data_by_id(
        self, user_ids: Iterable[UserID]
    ) -> dict[UUID, UserCardData]: ...
