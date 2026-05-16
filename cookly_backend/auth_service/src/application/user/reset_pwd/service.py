from abc import ABC, abstractmethod
from typing import NewType
from uuid import UUID

ResetPasswordCode = NewType("ResetPasswordCode", str)
ResetPasswordToken = NewType("ResetPasswordToken", str)


class ResetPwdService(ABC):
    @abstractmethod
    async def save_password_reset_code(
        self, user_id: UUID, code: ResetPasswordCode
    ) -> None: ...

    @abstractmethod
    async def get_user_id_from_reset_pwd_code(
        self, code: ResetPasswordCode
    ) -> UUID | None: ...

    @abstractmethod
    async def delete_reset_pwd_code(self, code: ResetPasswordCode) -> None: ...

    @abstractmethod
    async def generate_reset_token(
        self, user_id: UUID
    ) -> ResetPasswordToken: ...

    @abstractmethod
    async def get_user_id_from_reset_token(
        self, token: ResetPasswordToken
    ) -> UUID | None: ...

    @abstractmethod
    async def delete_reset_token(self, token: ResetPasswordToken) -> None: ...
