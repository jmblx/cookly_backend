from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from domain.entities.value_objects import PubRecipeRequestStatus
from presentation.web_api.responses import BaseResponse


class PublishRecipeRequestResponse(BaseModel):
    pub_recipe_request_id: int


class RecipeRequestResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    feedback: str | None
    status: PubRecipeRequestStatus
    reviewed_at: datetime | None
    created_at: datetime
    recipe_id: int


class RejectPubRecipeRequestData(BaseModel):
    feedback: str | None = Field(default=None)
