from dishka import Provider, Scope, provide

from application.auth.login_handler import LoginHandler
from application.ingredient.get_all_ingredient_groups import GetAllIngredientGroupsHandler
from application.ingredient.search_ingredients import SearchIngredientsHandler
from application.pub_recipe_request.approve_pub_recipe_request import ApprovePubRecipeRequestHandler
from application.pub_recipe_request.delete_pub_recipe_request import DeletePubRecipeRequestHandler
from application.pub_recipe_request.reject_pub_recipe_request import RejectPubRecipeRequestHandler
from application.pub_recipe_request.request_publish_request import CreateRequestPublishRecipeHandler
from application.recipe.add_to_favorite import SetRecipeIsFavoriteHandler
from application.recipe.categories.get_all import GetAllRecipeCategoriesHandler
from application.recipe.categories.search_category import SearchRecipeCategoryHandler
from application.recipe.cooking_sessions.cancel_cooking_session import CancelCookingSessionHandler
from application.recipe.cooking_sessions.change_active_step import ChangeStepCookingSessionHandler
from application.recipe.cooking_sessions.finish_cooking_session import FinishCookingSessionHandler
from application.recipe.cooking_sessions.get_user_active_session import GetUserCookingSessionHandler
from application.recipe.cooking_sessions.start_cooking_session import StartCookingSessionHandler
from application.recipe.create_recipe import CreateRecipeHandler
from application.recipe.delete_recipe import DeleteRecipeHandler
from application.recipe.get_feed import GetFeedHandler
from application.recipe.get_meal_tt_feed import GetMealTimeTypeFeedHandler
from application.recipe.get_recipe import GetRecipeHandler
from application.recipe.search_recipes import SearchRecipesHandler
from application.recipe.set_recipe_image import SetRecipeImageHandler
from application.recipe.set_recipe_rate import AddRecipeRateHandler
from application.recipe.set_recipe_step_image import SetRecipeStepImageHandler
from application.recipe.update_recipe import UpdateRecipeHandler
from application.user.get_favorites import GetUserFavoriteRecipesHandler
from application.user.get_history import GetUserRecipeHistoryHandler
from application.user.set_excluded_ingredient_groups import SetExcludedIngredientGroupsHandler


class HandlerProvider(Provider):
    get_login_handler = provide(LoginHandler, scope=Scope.REQUEST)
    create_recipe_handler = provide(CreateRecipeHandler, scope=Scope.REQUEST)
    set_recipe_image_handler = provide(SetRecipeImageHandler, scope=Scope.REQUEST)
    set_recipe_step_image_handler = provide(SetRecipeStepImageHandler, scope=Scope.REQUEST)
    update_recipe_handler = provide(UpdateRecipeHandler, scope=Scope.REQUEST)
    delete_recipe_handler = provide(DeleteRecipeHandler, scope=Scope.REQUEST)
    search_ingredients_handler = provide(SearchIngredientsHandler, scope=Scope.REQUEST)
    search_recipe_category_handler = provide(SearchRecipeCategoryHandler, scope=Scope.REQUEST)
    get_recipe_handler = provide(GetRecipeHandler, scope=Scope.REQUEST)
    set_excluded_ingredient_groups = provide(SetExcludedIngredientGroupsHandler, scope=Scope.REQUEST)
    get_all_recipe_category_handler = provide(GetAllRecipeCategoriesHandler, scope=Scope.REQUEST)
    get_all_ingredient_groups_handler = provide(GetAllIngredientGroupsHandler, scope=Scope.REQUEST)
    get_feed_handler = provide(GetFeedHandler, scope=Scope.REQUEST)
    get_meal_time_type_feed_handler = provide(GetMealTimeTypeFeedHandler, scope=Scope.REQUEST)
    start_cooking_session = provide(StartCookingSessionHandler, scope=Scope.REQUEST)
    get_user_cooking_session_handler = provide(GetUserCookingSessionHandler, scope=Scope.REQUEST)
    change_step_cooking_session_handler = provide(ChangeStepCookingSessionHandler, scope=Scope.REQUEST)
    cancel_cooking_session_handler = provide(CancelCookingSessionHandler, scope=Scope.REQUEST)
    finish_cooking_session_handler = provide(FinishCookingSessionHandler, scope=Scope.REQUEST)
    add_recipe_to_favorite_handler = provide(SetRecipeIsFavoriteHandler, scope=Scope.REQUEST)
    add_recipe_rate_handler = provide(AddRecipeRateHandler, scope=Scope.REQUEST)
    get_user_recipe_history_handler = provide(GetUserRecipeHistoryHandler, scope=Scope.REQUEST)
    get_user_favorite_recipes_handler = provide(GetUserFavoriteRecipesHandler, scope=Scope.REQUEST)
    search_recipes_handler = provide(SearchRecipesHandler, scope=Scope.REQUEST)

    request_publish_recipe_handler = provide(CreateRequestPublishRecipeHandler, scope=Scope.REQUEST)
    approve_pub_recipe_request_handler = provide(ApprovePubRecipeRequestHandler, scope=Scope.REQUEST)
    reject_pub_recipe_request_handler = provide(RejectPubRecipeRequestHandler, scope=Scope.REQUEST)
    delete_pub_recipe_request_handler = provide(DeletePubRecipeRequestHandler, scope=Scope.REQUEST)
