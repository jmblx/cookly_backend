from typing import TypedDict


class RoleView(TypedDict):
    name: str
    base_scopes: list[str]
    is_base: bool


class RoleViewWithId(RoleView):
    id: int
