from pydantic import BaseModel

from domain.entities.resource_server.value_objects import ResourceServerType


class ClientAuthResponseModel(BaseModel):
    client_name: str


class RoleViewModel(BaseModel):
    name: str
    base_scopes: list[str]
    is_base: bool


class RoleViewWithIdModel(RoleViewModel):
    id: int


class ResourceServerViewModel(BaseModel):
    name: str
    type: ResourceServerType
    roles: list[RoleViewWithIdModel] | None = None


# class UpdateResourceServerModel(BaseModel):
#     name: str | None
#     base_url: str | None
#     allowed_urls: list[str] | None
#     client_type: ClientTypeEnum | None
class UpdateResourceServerModel(BaseModel):
    new_name: str | None
    new_type: ResourceServerType | None
