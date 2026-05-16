from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.interfaces.role_repo import RoleRepository
from application.common.interfaces.user_repo import UserRepository
from application.user.common.user_service import UserService
from domain.entities.user.model import User
from infrastructure.db.models.secondary import user_role_association


class UserServiceImpl(UserService):
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        session: AsyncSession,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.session = session

    # async def add_rs_to_user(
    #     self, user: User, resource_server: ResourceServer
    # ):
    #     user.resource_servers.append(client)
    #     await self.user_repository.save(user)
    #     new_roles = await self.role_repository.get_base_client_roles(
    #         client_id=client.id
    #     )
    #     await self.user_repository.add_roles_to_user(
    #         user.id, [role.id for role in new_roles]
    #     )

    async def add_rs_by_ids_to_user(self, user: User, rs_ids: list[int]):
        if not rs_ids:
            return

        existing_rs = await self.session.execute(
            select(user_rs.c.rs_id).where(
                user_rs.c.user_id == user_id, user_rs.c.rs_id.in_(rs_ids)
            )
        )
        existing_rs_ids = {row.rs_id for row in existing_rs}

        existing_roles = await self.session.execute(
            select(user_role_association.c.role_id)
            .where(user_role.c.user_id == user_id)
            .where(
                user_role.c.role_id.in_(
                    select(role.c.id).where(role.c.rs_id.in_(rs_ids))
                )
            )
        )
        existing_role_ids = {row.role_id for row in existing_roles}

        # 2. Добавляем новые связи
        new_rs_ids = set(rs_ids) - existing_rs_ids
        if new_rs_ids:
            await self.session.execute(
                insert(user_rs).from_select(
                    [user_rs.c.user_id, user_rs.c.rs_id],
                    select(user_id, resource_server.c.id).where(
                        resource_server.c.id.in_(new_rs_ids)
                    ),
                )
            )

        new_roles = await self.session.execute(
            select(role.c.id).where(role.c.rs_id.in_(rs_ids))
        )
        new_role_ids = {row.id for row in new_roles} - existing_role_ids

        if new_role_ids:
            await self.session.execute(
                insert(user_role).from_select(
                    [user_role.c.user_id, user_role.c.role_id],
                    select(user_id, role.c.id).where(
                        role.c.id.in_(new_role_ids)
                    ),
                )
            )
