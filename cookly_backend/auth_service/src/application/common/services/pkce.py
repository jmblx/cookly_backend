import base64
import hashlib
import os
from dataclasses import dataclass
from enum import StrEnum


class PKCECodeChallengeMethod(StrEnum):
    """Определение допустимых методов хеширования для PKCE"""

    S256 = "S256"
    plain = "plain"


@dataclass
class PKCEData:
    code_verifier: str
    code_challenge_method: PKCECodeChallengeMethod = (
        PKCECodeChallengeMethod.S256
    )

    def __post_init__(self) -> None:
        """Валидация данных PKCE"""
        if not self.is_valid_code_verifier(self.code_verifier):
            raise ValueError(
                "Invalid code_verifier: must be between 43 and 128 characters."
            )

        if self.code_challenge_method not in PKCECodeChallengeMethod:
            raise ValueError(
                f"Invalid code_challenge_method: {self.code_challenge_method}. Must be one of {list(PKCECodeChallengeMethod)}."
            )

    @staticmethod
    def is_valid_code_verifier(code_verifier: str) -> bool:
        """
        Валидация code_verifier по стандартам PKCE:
        - Должен быть длиной от 43 до 128 символов.
        - Должен содержать только символы [A-Z, a-z, 0-9, "-", ".", "_", "~"]
        """
        if not (43 <= len(code_verifier) <= 128):
            return False
        valid_characters = set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
        )
        return all(c in valid_characters for c in code_verifier)


class PKCEService:
    @staticmethod
    def generate_code_verifier() -> str:
        """
        Генерация случайного `code_verifier` согласно рекомендациям PKCE (32 байта).
        """
        return (
            base64.urlsafe_b64encode(os.urandom(32))
            .decode("utf-8")
            .rstrip("=")
        )

    @staticmethod
    def generate_code_challenge(pkce_data: PKCEData) -> str:
        """
        Генерация `code_challenge` на основе данных PKCE, переданных через PKCEData.
        """
        if pkce_data.code_challenge_method == PKCECodeChallengeMethod.S256:
            sha256_hash = hashlib.sha256(
                pkce_data.code_verifier.encode("utf-8")
            ).digest()
            return (
                base64.urlsafe_b64encode(sha256_hash)
                .decode("utf-8")
                .rstrip("=")
            )
        elif pkce_data.code_challenge_method == PKCECodeChallengeMethod.plain:
            return pkce_data.code_verifier
        else:
            raise ValueError(
                f"Unsupported code_challenge_method: {pkce_data.code_challenge_method}"
            )
