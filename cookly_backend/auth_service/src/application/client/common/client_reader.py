from abc import ABC, abstractmethod
from dataclasses import dataclass

from application.common.views.client_view import ClientsIdsData, ClientView
from domain.entities.client.value_objects import ClientID


@dataclass
class ClientAuthData:
    client_name: str
    allowed_redirect_urls: list[str]


class ClientReader(ABC):
    @abstractmethod
    async def read_for_auth_page(
        self, client_id: ClientID
    ) -> ClientAuthData | None: ...

    @abstractmethod
    async def read_for_client_page(
        self, client_id: ClientID
    ) -> ClientView | None: ...

    @abstractmethod
    async def read_all_clients_ids_data(
        self, from_: int, limit: int
    ) -> dict[ClientID, ClientsIdsData]: ...

    @abstractmethod
    async def find_by_marks(
        self, search_input: str, similarity: float = 0.3
    ) -> dict[ClientID, ClientsIdsData] | None: ...
