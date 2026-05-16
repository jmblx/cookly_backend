from typing import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.user_reader import (
    UserCardData,
    UserReader,
)
from domain.entities.user.model import User
from domain.entities.user.value_objects import UserID


class UserReaderImpl(UserReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_card_data_by_id(
        self, user_ids: Iterable[UserID]
    ) -> dict[UUID, UserCardData]:
        query = select(User.id, User.email).where(
            User._id.in_([uid.value for uid in user_ids])
        )
        user_card_data = (await self.session.execute(query)).all()
        return {
            user.id.value: {"email": user.email.value}
            for user in user_card_data
        }
