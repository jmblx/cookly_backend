from application.client.client_ref.common.reader import RefReader
from presentation.web_api.routes.client.refs.models import RefView


class ReadRefPageViewQueryHandler:
    def __init__(self, ref_reader: RefReader):
        self.ref_reader = ref_reader

    async def handle(self, ref_id: int) -> RefView:
        return await self.ref_reader.read_ref_page_view(ref_id)
