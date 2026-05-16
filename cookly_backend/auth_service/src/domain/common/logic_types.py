from typing import Literal, get_args

UserScope = Literal["email", "avatar_path"]
ALLOWED_SCOPES: list[str] = list(get_args(UserScope))
