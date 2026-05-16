from uuid import UUID, uuid4

import pytest

from domain.common.services.pwd_service import PasswordHasher
from domain.entities.user.model import User
from domain.entities.user.value_objects import Email
from infrastructure.db.repositories.user_repo_impl import UserRepositoryImpl


@pytest.mark.asyncio
async def test_user_repo_update(
    async_session, real_user_repo: UserRepositoryImpl, user_in_db: User
):
    new_user_email = Email("new_test_user_email@gmail.com")
    user_id = user_in_db.id
    user_in_db.email = new_user_email
    await real_user_repo.save(user_in_db)
    await async_session.commit()
    assert user_in_db.email == new_user_email
    assert user_id == user_in_db.id


@pytest.mark.asyncio
async def test_user_repo_add(
    async_session,
    real_user_repo: UserRepositoryImpl,
    static_entities,
    ph: PasswordHasher,
):
    user_data = static_entities["user"]
    user_data["email"] = f"q{user_data["email"]}"
    user_data["user_id"] = uuid4()
    user = User.create(**user_data, password_hasher=ph)
    await real_user_repo.save(user)
    await async_session.commit()
    assert type(user.id.value) is UUID
    assert user.is_email_confirmed == False
