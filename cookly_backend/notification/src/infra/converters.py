from adaptix.conversion import get_converter

from src.application.email_notification.email_confirmation.handler import EmailConfirmationCommand
from src.presentation.schemas import EmailConfirmationSchema

email_confirmation_dto_convert = get_converter(
    src=EmailConfirmationSchema,
    dst=EmailConfirmationCommand,
)
