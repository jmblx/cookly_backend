from dataclasses import dataclass
from typing import Literal

from src.application.email_notification.smtp_service import SmtpService
from src.config import ApiPathsConfig


@dataclass
class ThirdPartyRegisterCommand:
    email: str
    generated_password: str
    provider: Literal["yandex"]


class ThirdPartyRegisterHandler:
    def __init__(self, smtp_service: SmtpService, api_paths_conf: ApiPathsConfig):
        self.smtp_service = smtp_service
        self.api_paths_conf = api_paths_conf

    async def handle(self, command: ThirdPartyRegisterCommand):
        body = f"""
            Здравствуйте! Вы зарегистрировались в приложении AuthCore через {command.provider},
            в связи с этим мы сгенерировали для вас пароль, который вы можете использовать для входа - {command.generated_password}\n
            Вы также можете изменить его в профиле.
        """
        await self.smtp_service.send_email(command.email, "Приветствуем в AuthCore", body)
