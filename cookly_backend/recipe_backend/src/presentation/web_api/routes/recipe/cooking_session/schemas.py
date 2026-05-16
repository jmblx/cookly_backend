from pydantic import BaseModel, ConfigDict, computed_field

from core.config import config_loader


class StartCookingSessionResponse(BaseModel):
    cooking_session_id: int


class CookingSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    current_step: int


class ActiveCookingSessionResponse(BaseModel):
    session: CookingSessionResponse
    recipe_id: int
    recipe_title: str
    step_title: str

    @computed_field
    @property
    def recipe_image_url(self) -> str | None:
        minio_config = config_loader.app_config.minio
        if not self.recipe_id:
            return None
        return f"{minio_config.url}/{minio_config.recipe_bucket_name}/{self.recipe_id}.webp"
