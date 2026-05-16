from application.common.idp import IdentityProvider
from application.common.interfaces.uow import Uow
from application.user.common.service import UserService


class SetExcludedIngredientGroupsHandler:
    def __init__(self, user_service: UserService, idp: IdentityProvider, uow: Uow):
        self.user_service = user_service
        self.idp = idp
        self.uow = uow

    async def handle(self, excluded_ingredient_groups: list[int]):
        user_id = await self.idp.get_current_user_id()
        await self.user_service.set_user_excluded_ingredient_groups(user_id, excluded_ingredient_groups)
        await self.uow.commit()
