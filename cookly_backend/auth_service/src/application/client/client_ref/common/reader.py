from abc import abstractmethod, ABC

from presentation.web_api.routes.client.refs.models import RefView


class RefReader(ABC):
    @abstractmethod
    async def read_ref_page_view(
        self, ref_id: int
    ) -> RefView | None: ...
