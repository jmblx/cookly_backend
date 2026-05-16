from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, computed_field

from core.config import config_loader
from domain.entities.value_objects import MealTimeType
from presentation.web_api.responses import BaseResponse
from presentation.web_api.routes.recipe.pub_recipe_request.schemas import RecipeRequestResponse


class ImagePathResponse(BaseModel):
    image_path: AnyHttpUrl


class IngredientResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    default_unit_measurement: str | None = None
    created_at: datetime


class RecipeStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    number: int

    @computed_field
    @property
    def image_url(self) -> str | None:
        minio_config = config_loader.app_config.minio
        if not self.id:
            return None
        return f"{minio_config.url}/{minio_config.recipe_step_bucket_name}/{self.id}.webp"


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient: IngredientResponse
    unit_measurement: str
    quantity: float


class RecipeCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class RecipeStepRequest(BaseModel):
    title: str
    description: str
    number: int


class RecipeIngredientRequest(BaseModel):
    ingredient_id: int
    unit_measurement: str | None = None
    quantity: float


class RecipeRequest(BaseModel):
    title: str
    description: str
    estimated_time: int
    calories_by_100grams: float
    meal_time: MealTimeType
    spicy_level: int = Field(le=5)
    difficulty_level: int = Field(le=5)
    steps: list[RecipeStepRequest]
    recipe_ingredients: list[RecipeIngredientRequest]
    recipe_categories_ids: list[int]


class RecipeFullRequest(RecipeRequest):
    author_id: UUID


class RecipeResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    author_id: UUID
    estimated_time: int
    calories_by_100grams: float
    meal_time: MealTimeType
    rating_sum: float
    rating_count: int
    is_public: bool
    spicy_level: int
    difficulty_level: int
    created_at: datetime

    steps: list[RecipeStepResponse]
    recipe_ingredients: list[RecipeIngredientResponse]
    recipe_categories: list[RecipeCategoryResponse]

    @computed_field
    @property
    def image_url(self) -> str | None:
        minio_config = config_loader.app_config.minio
        if not self.id:
            return None
        return f"{minio_config.url}/{minio_config.recipe_bucket_name}/{self.id}.webp"


class UserRecipeResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    recipe: RecipeResponse
    pub_recipe_request: RecipeRequestResponse | None
    existed_cooking_session: bool
    is_author: bool
    is_favorite: bool
    user_rate: int | None


class RecipeCardResponse(BaseResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    estimated_time: int
    calories_by_100grams: float
    meal_time: MealTimeType
    rating_sum: float
    rating_count: int
    spicy_level: int
    difficulty_level: int

    @computed_field
    @property
    def image_url(self) -> str | None:
        minio_config = config_loader.app_config.minio
        if not self.id:
            return None
        return f"{minio_config.url}/{minio_config.recipe_bucket_name}/{self.id}.webp"


class FeedResponse(BaseResponse):
    recipes: list[RecipeCardResponse] | None
    last_recipe_score: float | None
    last_recipe_id: int | None
    pagination_key: str | None


class DefaultRecipesResponse(BaseResponse):
    recipes: list[RecipeCardResponse] | None


class FeedPaginationParams(BaseModel):
    last_score: float | None = Field(default=None)
    last_id: int | None = Field(default=None)
    pagination_key: str | None = Field(default=None)
    limit: int = Field(default=20)


class IngredientGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class UserIngredientGroupResponse(IngredientGroupResponse):
    model_config = ConfigDict(from_attributes=True)

    excluded_by_user: bool


class SearchRecipeQuery(BaseModel):
    query: str | None = Field(default=None)
    include_ingredient_group_ids: list[int] | None = Field(default=None)
    max_spicy: int | None = Field(default=None)
    max_difficulty: int | None = Field(default=None)
    max_calories_by_100grams: float | None = Field(default=None)
    meal_time_type: MealTimeType | list[MealTimeType] = Field(default=None)
    min_avg_rating: float | None = Field(default=None)
    max_estimated_cooking_time: int | None = Field(default=None)
    limit: int = Field(default=100)
    offset: int = Field(default=0)
