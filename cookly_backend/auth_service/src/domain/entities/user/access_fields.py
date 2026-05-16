from typing import TypedDict

from domain.entities.role.value_objects import RoleID
from domain.entities.user.value_objects import UserID


class UserAccessFields(TypedDict):
    id: UserID
    role_id: RoleID
