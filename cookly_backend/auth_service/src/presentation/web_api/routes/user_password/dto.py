from dataclasses import dataclass


@dataclass
class ResetPasswordDTO:
    new_password: str
