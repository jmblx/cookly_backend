import logging
from dataclasses import dataclass

from application.client.common.client_reader import ClientReader
from application.common.interfaces.imedia_storage import ClientS3StorageService
from application.common.views.client_view import ClientView
from domain.entities.client.value_objects import ClientID

logger = logging.getLogger(__name__)


@dataclass
class ReadClientPageViewQuery:
    client_id: int
    load_avatar: bool


class ReadClientPageViewQueryHandler:
    def __init__(
        self,
        client_reader: ClientReader,
        client_storage: ClientS3StorageService,
    ):
        self.client_reader = client_reader
        self.client_storage = client_storage

    async def handle(self, query: ReadClientPageViewQuery) -> ClientView:
        client_data: ClientView = (
            await self.client_reader.read_for_client_page(
                ClientID(query.client_id)
            )
        )
        if query.load_avatar:
            presigned_url = self.client_storage.get_presigned_avatar_url(
                str(query.client_id)
            )
            # logger.info(f"client presigned_url={presigned_url}")
            client_data = dict(**client_data, avatar_url=presigned_url)

        return client_data
