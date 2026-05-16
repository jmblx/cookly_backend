from dataclasses import dataclass, field

from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.role.value_objects import (
    RoleBaseScopes,
    RoleID,
    RoleName,
)


@dataclass
class Role:
    id: RoleID = field(init=False)
    name: RoleName
    base_scopes: RoleBaseScopes
    rs_id: ResourceServerID
    is_base: bool
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        base_scopes: dict[str, str],
        rs_id: int,
        is_base: bool = False,
    ) -> "Role":
        return cls(
            name=RoleName(name),
            base_scopes=RoleBaseScopes.create(base_scopes),
            rs_id=ResourceServerID(rs_id),
            is_base=is_base,
        )
