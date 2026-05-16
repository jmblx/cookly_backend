from dishka import Provider, Scope, provide

from infrastructure.bot.recipe_bot import RecipeBot
from infrastructure.bot.search_param_extractor import OllamaRecipeExtractor


class SearchRecipeBotProvider(Provider):
    recipe_search_params_extractor = provide(OllamaRecipeExtractor, scope=Scope.REQUEST)
    recipe_bot = provide(RecipeBot, scope=Scope.REQUEST)
