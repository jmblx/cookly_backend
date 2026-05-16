from pydantic import BaseModel


class UpdateRole(BaseModel):
    new_name: str | None = None
    new_base_scopes: dict[str, str] | None = None
    new_is_base: bool | None = None
