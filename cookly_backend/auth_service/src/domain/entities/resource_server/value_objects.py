from enum import StrEnum
from typing import NewType

ResourceServerID = NewType("ClientID", int)


class ResourceServerType(StrEnum):
    RBAC_BY_AS = "RBAC_BY_AS"
    RS_CONTROLLED = "RS_CONTROLLED"


ResourceServerIds = list[ResourceServerID]
