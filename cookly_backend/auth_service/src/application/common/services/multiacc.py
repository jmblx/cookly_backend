from application.common.id_provider import UserIdentityProvider
from domain.entities.user.model import User
from domain.entities.user.value_objects import UserID


async def change_active_account_id(
    base_idp: UserIdentityProvider, new_active_user: User
) -> tuple[UserID | None, UserID | None]:
    current_active_account_id = await base_idp.get_current_user_id()
    is_switching_account = (
        current_active_account_id is not None
        and current_active_account_id != new_active_user.id
    )
    previous_account_id = (
        current_active_account_id if is_switching_account else None
    )
    new_account_id = (
        new_active_user.id if current_active_account_id is not None else None
    )
    return previous_account_id, new_account_id
