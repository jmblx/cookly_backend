import argon2
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.value_objects import HashedPassword, RawPassword
from domain.exceptions.pwd_hasher import PasswordMismatchError


class PasswordHasherImpl(PasswordHasher):
    def __init__(self, ph: argon2.PasswordHasher) -> None:
        self.ph = ph

    def hash_password(self, raw_password: RawPassword) -> HashedPassword:
        return HashedPassword(self.ph.hash(raw_password.value))

    def check_password(
        self, plain_password: RawPassword, hashed_password: HashedPassword
    ) -> None:
        try:
            self.ph.verify(hashed_password.value, plain_password.value)
        except VerifyMismatchError as exc:
            raise PasswordMismatchError from exc


pwd_hasher = PasswordHasherImpl(Argon2Hasher())
print(pwd_hasher.hash_password(RawPassword("string")))
