from abc import ABC, abstractmethod
from typing import Literal, TypedDict
from uuid import UUID, uuid4

from domain.common.logic_types import UserScope
from domain.entities.resource_server.value_objects import ResourceServerIds


class RequiredResources(TypedDict, total=False):
    user_data_needed: list[UserScope]
    rs_ids: ResourceServerIds


class AllowToClientTokenData(RequiredResources):
    redirect_url: str


class AllowClientAccessService(ABC):

    @staticmethod
    def generate_allow_to_client_token():
        return uuid4()

    @abstractmethod
    async def save_allow_to_client_token_data(
        self,
        allow_to_client_token: UUID,
        required_resources: AllowToClientTokenData,
    ): ...
