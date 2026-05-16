from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.client.ref_model import ClientRef


@dataclass(frozen=True)
class SaveRefDTO:
    ref_id: int


class RefRepository(ABC):
    @abstractmethod
    async def save(self, client: ClientRef) -> SaveRefDTO:
        pass

    @abstractmethod
    async def get_by_id(self, ref_id: int) -> ClientRef | None:
        pass
