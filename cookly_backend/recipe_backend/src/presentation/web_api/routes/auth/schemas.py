from uuid import UUID

from pydantic import BaseModel, EmailStr

from domain.entities.value_objects import RoleType


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: int
    session_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: int
    session_token: str


class MeResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: RoleType
    avatar_url: str | None
