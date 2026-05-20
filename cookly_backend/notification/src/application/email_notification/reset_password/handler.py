from dataclasses import dataclass

from src.application.email_notification.smtp_service import SmtpService
from src.config import ApiPathsConfig

@dataclass
class ResetPasswordCommand:
    email: str
    reset_password_token: str

class ResetPasswordHandler:
    def __init__(self, smtp_service: SmtpService, api_paths_conf: ApiPathsConfig):
        self.smtp_service = smtp_service
        self.api_paths_conf = api_paths_conf

    async def handle(self, command: ResetPasswordCommand):
        body = f"""
        Код на смену пароля в Cookly:
        {command.reset_password_token}
        его срок действия - 15 минут
        если не вы запросили код, то возможно к вашему аккаунту пытаются
        получить доступ злоумышленники."""
        await self.smtp_service.send_email(command.email, "Сброс пароля", body)
