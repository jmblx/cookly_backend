from dishka import Provider, Scope, provide

from application.common.idp import IdentityProvider
from application.common.interfaces.idp_service import IDPService
from application.common.interfaces.s3_storage import S3Storage
from application.pub_recipe_request.common.service import PubRecipeRequestService
from application.recipe.common.service import RecipeService
from application.recipe.cooking_sessions.service import CookingService
from application.user.common.preference_service import PreferenceProfileService
from application.user.common.service import UserService
from infrastructure.services.idp_service import AuthCoreIDPService
from infrastructure.services.jwt_service import JWTService
from infrastructure.services.minio_service import MinioService


class ServicesProvider(Provider):
    identity_provider = provide(IdentityProvider, scope=Scope.REQUEST, provides=IdentityProvider)
    idp_service = provide(AuthCoreIDPService, scope=Scope.REQUEST, provides=IDPService)
    jwt_service = provide(JWTService, scope=Scope.APP)
    recipe_service = provide(RecipeService, scope=Scope.REQUEST, provides=RecipeService)
    user_service = provide(UserService, scope=Scope.REQUEST, provides=UserService)
    minio_service = provide(MinioService, scope=Scope.REQUEST, provides=S3Storage)
    cooking_service = provide(CookingService, scope=Scope.REQUEST, provides=CookingService)
    pub_recipe_request_service = provide(PubRecipeRequestService, scope=Scope.REQUEST)
    preference_profile_service = provide(PreferenceProfileService, scope=Scope.REQUEST)
