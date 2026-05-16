from typing import TypedDict

from pydantic import BaseModel

from domain.common.logic_types import UserScope
from application.common.views.rs_view import ResourceServerIdsViewData
from domain.entities.client.value_objects import ClientName


class RegisterRefData(BaseModel):
    name: str
    user_scopes: list[UserScope]
    rs_ids: list[int]


class RefView(TypedDict):
    name: str
    user_scopes: list[UserScope]
    ref_resource_servers: ResourceServerIdsViewData
    client_name: str


class UpdateRefModel(BaseModel):
    name: str | None = None
    user_scopes: list[UserScope] | None = None
    rs_ids: list[int] | None = None
