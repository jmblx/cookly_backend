from dataclasses import dataclass
from typing import TypedDict, NewType

from domain.entities.client.value_objects import ClientTypeEnum
from presentation.web_api.routes.client.models import RefsIdsData


class ClientView(TypedDict, total=False):
    name: str
    base_url: str
    allowed_redirect_urls: list[str]
    type: ClientTypeEnum
    refs_ids_data: dict[int, RefsIdsData] | None
    avatar_url: str | None


@dataclass
class ClientsIdsData:
    name: str
