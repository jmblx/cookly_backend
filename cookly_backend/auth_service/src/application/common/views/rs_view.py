from dataclasses import dataclass
from typing import TypedDict

from application.common.views.role_view import RoleViewWithId
from domain.entities.resource_server.value_objects import ResourceServerType, ResourceServerID


class ResourceServerView(TypedDict, total=False):
    name: str
    type: ResourceServerType
    roles: list[RoleViewWithId]


@dataclass
class ResourceServerIdsData:
    name: str


ResourceServerIdsViewData = dict[ResourceServerID, ResourceServerIdsData]
