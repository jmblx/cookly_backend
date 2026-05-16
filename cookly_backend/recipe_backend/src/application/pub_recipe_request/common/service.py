from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from application.common.errors.exceptions import NotFoundError
from application.common.interfaces.uow import Uow
from application.recipe.common.service import RecipeService
from domain.entities.value_objects import PubRecipeRequestStatus
from infrastructure.db.gateways.pub_recipe_request import PubRecipeRequestGateway
from infrastructure.db.gateways.recipe_gateway import RecipeGateway
from infrastructure.db.models import PubRecipeRequest, Recipe


class PubRecipeRequestService:
    def __init__(
        self,
        session: AsyncSession,
        gateway: PubRecipeRequestGateway,
        recipe_gateway: RecipeGateway,
        recipe_service: RecipeService,
        uow: Uow,
        tz: ZoneInfo
    ):
        self.session = session
        self.gateway = gateway
        self.recipe_gateway = recipe_gateway
        self.recipe_service = recipe_service
        self.uow = uow
        self.tz = tz

    async def _create_pub_recipe_request(
        self, recipe: Recipe
    ) -> PubRecipeRequest:
        pub_recipe_request = PubRecipeRequest(
            recipe=recipe,
            author_id=recipe.author_id,
            created_at=datetime.now(tz=self.tz)
        )
        await self.gateway.save(pub_recipe_request)
        return pub_recipe_request

    async def create_pub_recipe_request(
        self, user_id: UUID, recipe_id: int,
    ) -> int:
        recipe = await self.recipe_service.get_with_author_check(recipe_id=recipe_id, user_id=user_id)
        pub_recipe_request = await self.renew_or_create_pub_recipe_request(recipe)
        return pub_recipe_request.id

    async def renew_or_create_pub_recipe_request(self, recipe: Recipe) -> PubRecipeRequest:
        recipe.is_public = False
        await self.recipe_gateway.save(recipe)
        pub_rq = await self.gateway.get_recipe_active_pub_rq(recipe.id)
        if not pub_rq:
            pub_rq = await self._create_pub_recipe_request(recipe)
        else:
            pub_rq.created_at = datetime.now(tz=self.tz)
            await self.gateway.save(pub_rq)
        return pub_rq

    async def renew_recipe_pub_rq_if_exists(self, recipe: Recipe) -> PubRecipeRequest | None:
        recipe.is_public = False
        await self.recipe_gateway.save(recipe)
        pub_rq = await self.gateway.get_recipe_active_pub_rq(recipe.id)
        if not pub_rq:
            return None
        pub_rq.created_at = datetime.now(tz=self.tz)
        await self.gateway.save(pub_rq)
        return pub_rq

    async def get_pub_recipe_request(self, pub_recipe_request_id: int) -> PubRecipeRequest:
        pub_recipe_request = await self.gateway.get_active_pub_rq_or_none(pub_recipe_request_id)
        if not pub_recipe_request:
            raise NotFoundError("active pub recipe request does not exist")
        return pub_recipe_request

    async def approve_recipe_request(self, pub_recipe_request_id: int, reviewer_id: UUID):
        pub_recipe_request = await self.get_pub_recipe_request(pub_recipe_request_id)

        pub_recipe_request.reviewed_at = datetime.now(tz=self.tz)
        pub_recipe_request.status = PubRecipeRequestStatus.approved.value
        pub_recipe_request.moderator_id = reviewer_id

        await self.gateway.save(pub_recipe_request)

        pub_recipe_request.recipe.is_public = True
        await self.recipe_gateway.save(pub_recipe_request.recipe)

    async def reject_recipe_request(self, pub_recipe_request_id: int, reviewer_id: UUID, feedback: str | None):
        pub_recipe_request = await self.get_pub_recipe_request(pub_recipe_request_id)

        pub_recipe_request.reviewed_at = datetime.now(tz=self.tz)
        pub_recipe_request.status = PubRecipeRequestStatus.rejected.value
        pub_recipe_request.moderator_id = reviewer_id
        pub_recipe_request.feedback = feedback

        await self.gateway.save(pub_recipe_request)
        await self.recipe_gateway.save(pub_recipe_request.recipe)
