from dataclasses import dataclass

from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.imedia_storage import (
    SetAvatarResponse,
    UserS3StorageService,
)
from application.common.interfaces.user_repo import UserRepository
from application.dtos.set_image import ImageDTO


@dataclass
class SetUserAvatarCommand:
    image: ImageDTO


class SetUserAvatarHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        media_storage: UserS3StorageService,
        idp: UserIdentityProvider,
    ):
        self.user_repo = user_repo
        self.media_storage = media_storage
        self.idp = idp

    async def handle(
        self,
        command: SetUserAvatarCommand,
    ) -> SetAvatarResponse:
        user = await self.idp.get_current_user()
        new_avatar_data = await self.media_storage.set_avatar(
            content=command.image.content,
            content_type=command.image.content_type,
            object_id=str(user.id.value),
        )
        return new_avatar_data
