from abc import ABC, abstractmethod

from application.user.reset_pwd.service import ResetPasswordCode


class NotifyService(ABC):
    @abstractmethod
    async def pwd_reset_notify(
        self, user_email: str, reset_pwd_token: ResetPasswordCode
    ) -> None:
        pass
