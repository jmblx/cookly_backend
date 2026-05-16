from application.client.common.client_repo import ClientRepository
from application.common.interfaces.imedia_storage import ClientS3StorageService
from domain.entities.client.value_objects import ClientID
from domain.exceptions.client import ClientNotFound


class GetClientAvatarHandler:
    def __init__(
        self,
        client_storage: ClientS3StorageService,
        client_repo: ClientRepository,
    ):
        self.client_storage = client_storage
        self.client_repo = client_repo

    async def handle(self, client_id: int):
        client = await self.client_repo.get_by_id(ClientID(client_id))
        if not client:
            raise ClientNotFound()
        return self.client_storage.get_presigned_avatar_url(str(client_id))
