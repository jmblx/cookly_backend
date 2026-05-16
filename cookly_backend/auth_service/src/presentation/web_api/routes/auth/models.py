import re
from uuid import UUID

from pydantic import BaseModel, AnyUrl, field_validator

from application.client.client_queries import ValidateClientRequest
from domain.common.logic_types import UserScope
from application.common.services.pkce import PKCECodeChallengeMethod, PKCEData


class UserAuthRequest(ValidateClientRequest, PKCEData): ...


class RequiredResources(BaseModel):
    user_data_needed: list[UserScope] | None = None
    rs_ids: list[int] | None = None


class GetMePageDataSchema(BaseModel):
    ref_id: int
    redirect_url: str
    code_verifier: str
    code_challenge_method: PKCECodeChallengeMethod

    @field_validator('redirect_url')
    @classmethod
    def validate_redirect_url(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', v):
            raise ValueError('URL must contain a valid protocol (e.g., http://, https://, myapp://)')

        return v


class CodeToTokenResponseSchema(BaseModel):
    email: str | None
    avatar_path: str | None


class NewActiveUserSchema(BaseModel):
    new_active_user_id: UUID | None
