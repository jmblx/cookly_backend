from collections.abc import Sequence

import sqlalchemy.dialects.postgresql as sa_pg
from sqlalchemy import cast, insert, select
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from application.common.interfaces.user_repo import (
    IdentificationFields,
    UserRepository,
)
from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email, UserID
from infrastructure.db.models import role_table, rs_table
from infrastructure.db.models.secondary import (
    user_role_association,
    user_rs_association_table,
)


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: User) -> None:
        await self.session.merge(user)

    async def delete(self, user: User) -> None:
        await self.session.delete(user)

    async def get_by_fields_with_clients(
        self, fields: IdentificationFields
    ) -> User | None:
        query = select(User).options(joinedload(User.clients))

        for field, value in fields.items():
            if hasattr(User, field):
                query = query.where(getattr(User, field) == value)

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, user_id: UserID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: Email) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def add_roles_to_user(
        self, user_id: UserID, role_ids: list[int]
    ) -> None:
        if not role_ids:
            return

        values = [
            {"user_id": user_id.value, "role_id": role_id}
            for role_id in role_ids
        ]

        stmt = (
            sa_pg.insert(user_role_association)
            .values(values)
            .on_conflict_do_nothing()
        )

        await self.session.execute(stmt)

    async def add_rs_to_user(
        self, user_id: UserID, rs_ids: Sequence[ResourceServerID]
    ) -> None:
        user_uuid = user_id.value

        existing_rs = await self.session.execute(
            select(user_rs_association_table.c.rs_id).where(
                user_rs_association_table.c.user_id == user_uuid,
                user_rs_association_table.c.rs_id.in_(rs_ids),
            )
        )
        existing_rs_ids = {row.rs_id for row in existing_rs}

        new_rs_ids = set(rs_ids) - existing_rs_ids

        if new_rs_ids:
            await self.session.execute(
                insert(user_rs_association_table).from_select(
                    [
                        user_rs_association_table.c.user_id,
                        user_rs_association_table.c.rs_id,
                    ],
                    select(
                        cast(user_uuid, PG_UUID), rs_table.c.id
                    ).where(  # Исправлено: PG_UUID вместо встроенного UUID
                        rs_table.c.id.in_(new_rs_ids)
                    ),
                )
            )

        existing_roles = await self.session.execute(
            select(user_role_association.c.role_id).where(
                user_role_association.c.user_id == user_uuid,
                user_role_association.c.role_id.in_(
                    select(role_table.c.id).where(
                        role_table.c.rs_id.in_(rs_ids),
                        role_table.c.is_base.is_(True),
                    )
                ),
            )
        )
        existing_role_ids = {row.role_id for row in existing_roles}

        new_roles = await self.session.execute(
            select(role_table.c.id).where(
                role_table.c.rs_id.in_(rs_ids), role_table.c.is_base.is_(True)
            )
        )
        new_role_ids = {row.id for row in new_roles} - existing_role_ids

        if new_role_ids:
            await self.session.execute(
                insert(user_role_association).from_select(
                    [
                        user_role_association.c.user_id,
                        user_role_association.c.role_id,
                    ],
                    select(
                        cast(user_uuid, PG_UUID), role_table.c.id
                    ).where(
                        role_table.c.id.in_(new_role_ids)
                    ),
                )
            )
