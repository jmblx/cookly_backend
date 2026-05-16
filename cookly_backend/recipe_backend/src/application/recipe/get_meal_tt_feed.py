from zoneinfo import ZoneInfo

from application.common.idp import IdentityProvider
from application.user.common.service import FeedData, UserService
from application.user.feed_utils import ScoreConfig
from domain.entities.value_objects import MealTimeType


class GetMealTimeTypeFeedHandler:
    def __init__(self, user_service: UserService, idp: IdentityProvider, tz: ZoneInfo):
        self.user_service = user_service
        self.idp = idp
        self.tz = tz

    async def handle(
        self,
        last_score: float | None,
        last_id: int | None,
        pagination_key: str | None,
        limit: int,
        meal_time_type: MealTimeType
    ) -> FeedData:
        user_id = await self.idp.get_current_user_id()
        config = ScoreConfig(
            rating_weight=0.6,
            meal_weight=0.3,
            random_weight=0.1,
            strict_meal=True
        )
        return await self.user_service.get_relevant_recipes(
            user_id,
            meal_time_type.value,
            last_score,
            last_id,
            pagination_key,
            limit,
            config
        )
