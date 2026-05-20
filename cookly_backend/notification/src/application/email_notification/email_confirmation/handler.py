from dataclasses import dataclass

from src.application.email_notification.smtp_service import SmtpService
from src.config import ApiPathsConfig


@dataclass
class EmailConfirmationCommand:
    email: str
    email_confirmation_token: str


class EmailConfirmationHandler:
    def __init__(self, smtp_service: SmtpService, api_paths_conf: ApiPathsConfig):
        self.smtp_service = smtp_service
        self.api_paths_conf = api_paths_conf

    async def handle(self, command: EmailConfirmationCommand):
        body = f"""
        Код подтверждения почты в Cookly:
        {command.email_confirmation_token}
        """
        await self.smtp_service.send_email(command.email, "Подтверждение почты", body)
