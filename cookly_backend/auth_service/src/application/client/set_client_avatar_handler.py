from dataclasses import dataclass
from datetime import datetime

from application.client.common.client_repo import ClientRepository
from application.common.interfaces.imedia_storage import ClientS3StorageService
from application.common.uow import Uow
from application.dtos.set_image import ImageDTO
from domain.entities.client.value_objects import ClientID
from domain.exceptions.client import ClientNotFound


@dataclass
class SetClientAvatarCommand:
    client_id: int
    image: ImageDTO


class SetClientAvatarHandler:
    def __init__(
        self,
        client_repo: ClientRepository,
        media_storage: ClientS3StorageService,
        uow: Uow,
    ):
        self.client_repo = client_repo
        self.media_storage = media_storage
        self.uow = uow

    async def handle(
        self,
        command: SetClientAvatarCommand,
    ) -> str:
        client = await self.client_repo.get_by_id(ClientID(command.client_id))
        if not client:
            raise ClientNotFound()
        client.avatar_upd_at = datetime.now()
        client_avatar_data = await self.media_storage.set_avatar(
            content=command.image.content,
            content_type=command.image.content_type,
            object_id=str(client.id),
        )
        await self.uow.commit()
        return client_avatar_data["avatar_presigned_url"]
