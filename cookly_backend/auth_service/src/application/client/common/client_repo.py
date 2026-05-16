from abc import ABC, abstractmethod

from application.dtos.client import ClientCreateDTO
from domain.entities.client.model import Client
from domain.entities.client.value_objects import ClientID


class ClientRepository(ABC):
    @abstractmethod
    async def save(self, client: Client) -> ClientCreateDTO:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: ClientID) -> Client | None:
        pass
