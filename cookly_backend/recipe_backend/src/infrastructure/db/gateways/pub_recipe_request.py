from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities.value_objects import PubRecipeRequestStatus
from infrastructure.db.models import PubRecipeRequest


class PubRecipeRequestGateway:
    def __init__(self, session: AsyncSession, tz: ZoneInfo):
        self.session = session
        self.tz = tz

    async def get_by_id(self, pub_recipe_request_id: int) -> PubRecipeRequest | None:
        return await self.session.get(PubRecipeRequest, pub_recipe_request_id)

    async def get_recipe_active_pub_rq(
        self,
        recipe_id: int,
        status: PubRecipeRequestStatus = PubRecipeRequestStatus.pending
    ) -> PubRecipeRequest | None:
        query = select(
            PubRecipeRequest
        ).where(
            PubRecipeRequest.recipe_id == recipe_id,
            PubRecipeRequest.status == status.value
        ).options(selectinload(PubRecipeRequest.recipe))
        return await self.session.scalar(query)

    async def get_active_pub_rq_or_none(
        self,
        pub_recipe_request_id: int,
        status: PubRecipeRequestStatus = PubRecipeRequestStatus.pending
    ) -> PubRecipeRequest | None:
        query = select(
            PubRecipeRequest
        ).where(
            PubRecipeRequest.id == pub_recipe_request_id,
            PubRecipeRequest.status == status.value
        ).options(selectinload(PubRecipeRequest.recipe))
        return await self.session.scalar(query)

    async def delete(self, pub_recipe_request: PubRecipeRequest):
        await self.session.delete(pub_recipe_request)
        await self.session.flush()

    async def save(self, pub_recipe_request: PubRecipeRequest) -> None:
        self.session.add(pub_recipe_request)
        await self.session.flush()
