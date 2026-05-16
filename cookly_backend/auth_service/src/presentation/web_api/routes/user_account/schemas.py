from uuid import UUID

from pydantic import BaseModel


class ClientGetUserDataInfo(BaseModel):
    email: str | None = None
    id: UUID
    avatar_path: str | None = None
