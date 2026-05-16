from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class ThirdPartyRegisterCommand:
    email: str
    generated_password: str
    provider: Literal["yandex"]


class ThirdPartyNotificationService(ABC):
    @abstractmethod
    async def send_register_notification(
        self, command: ThirdPartyRegisterCommand
    ) -> None: ...
