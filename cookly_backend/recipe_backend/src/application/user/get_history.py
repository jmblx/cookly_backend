from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from application.common.idp import IdentityProvider
from application.user.common.service import UserService
from infrastructure.db.models import Recipe


class GetUserRecipeHistoryHandler:
    def __init__(self, user_service: UserService, idp: IdentityProvider, tz: ZoneInfo, session: AsyncSession):
        self.user_service = user_service
        self.idp = idp
        self.tz = tz
        self.session = session


    async def handle(
        self,
    ) -> list[Recipe]:
        user_id = await self.idp.get_current_user_id()
        return await self.user_service.get_recipes_history(
            user_id,
        )
