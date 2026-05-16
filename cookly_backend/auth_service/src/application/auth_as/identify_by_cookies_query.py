from typing import TypedDict
from uuid import UUID

from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.imedia_storage import UserS3StorageService


class UserData(TypedDict):
    id: UUID
    email: str
    # avatar_path: str
    avatar_update_timestamp: int | None
    is_admin: bool


class IdentifyByCookiesQueryHandler:
    def __init__(
        self, idp: UserIdentityProvider, s3_storage: UserS3StorageService
    ):
        self.idp = idp
        self.s3_storage = s3_storage

    async def handle(self) -> UserData:
        user = await self.idp.get_current_user()
        avatar_update_timestamp = (
            await self.s3_storage.get_user_avatar_update_timestamp(
                str(user.id.value)
            )
        )
        return {
            "email": user.email.value,
            "id": user.id.value,
            # "avatar_path": self.s3_storage.get_presigned_avatar_url(str(user.id.value)),
            "avatar_update_timestamp": avatar_update_timestamp,
            "is_admin": user.is_admin,
        }
