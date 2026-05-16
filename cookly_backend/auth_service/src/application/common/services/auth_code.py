import uuid
from abc import ABC, abstractmethod
from typing import TypedDict

from domain.common.logic_types import UserScope
from domain.entities.client.ref_model import ClientRef
from domain.entities.resource_server.value_objects import ResourceServerIds


class AuthCodeDataInput(TypedDict, total=False):
    user_id: str
    code_challenger: str
    ref: ClientRef


class AuthCodeData(TypedDict, total=False):
    user_id: str
    client_id: str
    code_challenger: str
    user_data_needed: list[UserScope]
    rs_ids: ResourceServerIds


class AuthorizationCodeStorage(ABC):
    @abstractmethod
    async def store_auth_code_data(
        self, auth_code: str, data: AuthCodeDataInput, expiration_time: int = 600
    ) -> None:
        """
        Сохраняет данные, связанные с авторизационным кодом.
        """

    @abstractmethod
    async def retrieve_auth_code_data(
        self, auth_code: str
    ) -> AuthCodeData | None:
        """
        Извлекает и удаляет данные, связанные с авторизационным кодом.
        """

    @abstractmethod
    async def delete_auth_code_data(self, auth_code: str) -> None:
        pass

    def generate_auth_code(self) -> str:
        return str(uuid.uuid4())
