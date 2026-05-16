import logging
from dataclasses import dataclass
from typing import TypedDict, cast
from uuid import UUID

from application.common.auth_server_token_types import NonActiveRefreshTokens
from application.common.id_provider import UserIdentityProvider
from application.common.interfaces.imedia_storage import UserS3StorageService
from application.common.interfaces.user_reader import UserReader


@dataclass
class GetAvailableAccountsQuery:
    non_active_accounts: NonActiveRefreshTokens


class AvailableAccountData(TypedDict):
    email: str
    avatar_url: str


class GetAvailableAccountsResponse(TypedDict):
    accounts: dict[UUID, AvailableAccountData] | None
    active_account_id: UUID | None


log = logging.getLogger(__name__)


class GetAvailableAccountsHandler:
    def __init__(
        self,
        idp: UserIdentityProvider,
        user_reader: UserReader,
        s3_storage: UserS3StorageService,
    ):
        self.idp = idp
        self.user_reader = user_reader
        self.s3_storage = s3_storage

    async def handle(
        self, query: GetAvailableAccountsQuery
    ) -> GetAvailableAccountsResponse:
        current_user_id = await self.idp.get_current_user_id()
        users_ids = set(query.non_active_accounts.keys())
        log.info("Current user id: %s", current_user_id)
        if current_user_id:
            users_ids.add(current_user_id)

        accounts_data = cast(
            dict[UUID, AvailableAccountData],
            await self.user_reader.get_user_card_data_by_id(users_ids),
        )
        if accounts_data is not None:
            for account_id in accounts_data.keys():
                accounts_data[account_id]["avatar_url"] = (
                    self.s3_storage.get_presigned_avatar_url(str(account_id))
                )
            return GetAvailableAccountsResponse(
                accounts=accounts_data,
                active_account_id=(
                    current_user_id.value if current_user_id else None
                ),
            )
        return GetAvailableAccountsResponse(
            accounts={}, active_account_id=None
        )
