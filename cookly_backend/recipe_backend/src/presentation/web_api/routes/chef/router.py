from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from infrastructure.bot.recipe_bot import RecipeBot
from presentation.web_api.routes.chef.schemas import MessageRequest, RecipeBotResponse

chef_router = APIRouter(route_class=DishkaRoute, tags=["chef"])


MAX_USER_PROMPT_LENGTH = 1500


@chef_router.post("/chat")
async def chat_about_recipes(
    request: MessageRequest,
    bot: FromDishka[RecipeBot],
) -> RecipeBotResponse:
    if len(request.message) > MAX_USER_PROMPT_LENGTH:
        return RecipeBotResponse(
            is_food_related=False,
            text_response="⛔ ШЕФ РАЗРЕЗАЛ: ПРЕВЫШЕН ЛИМИТ В MAX_USER_PROMPT_LENGTH СИМВОЛОВ."
                          " УКОРОТИ СООБЩЕНИЕ, КАК ХВОСТ У ТРЕСКИ, И ПОПРОБУЙ СНОВА!",
            recipes=[],
        )
    result = await bot.process_message(request.message)
    return RecipeBotResponse(**result)
