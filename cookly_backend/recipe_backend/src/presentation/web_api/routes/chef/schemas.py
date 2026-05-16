from pydantic import BaseModel

from presentation.web_api.routes.recipe.schemas import RecipeCardResponse


class MessageRequest(BaseModel):
    message: str


class RecipeBotResponse(BaseModel):
    is_food_related: bool
    text_response: str
    recipes: list[RecipeCardResponse]
