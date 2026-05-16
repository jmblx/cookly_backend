"""squashed

Revision ID: 5596046d3be1
Revises: e363cbf19d66
Create Date: 2025-03-31 20:23:27.493040

"""

import os
from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from argon2 import PasswordHasher
from pydantic import BaseModel
from sqlalchemy.dialects import postgresql

from domain.entities.user.value_objects import RawPassword
from infrastructure.services.security.pwd_service import PasswordHasherImpl

# revision identifiers, used by Alembic.
revision: str = "5596046d3be1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class AdminSettings(BaseModel):
    admin_passwords: str = os.getenv("API_ADMIN_PASSWORDS", "")
    admin_emails: str = os.getenv("API_ADMIN_EMAILS", "")


def upgrade() -> None:
    op.create_table(
        "client",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column(
            "allowed_redirect_urls",
            postgresql.ARRAY(sa.String()),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum("PUBLIC", "PRIVATE", name="client_type_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("is_email_confirmed", sa.Boolean(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("avatar_path", sa.String(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "resource_server",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "RBAC_BY_AS", "RS_CONTROLLED", name="access_control_type_enum"
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "base_scopes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_base", sa.Boolean(), nullable=False),
        sa.Column("rs_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["rs_id"], ["resource_server.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_client_association",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["client.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_role_association",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "client_rs_association_table",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("rs_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["client.id"],
        ),
        sa.ForeignKeyConstraint(
            ["rs_id"],
            ["resource_server.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_rs_association_table",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rs_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["rs_id"], ["resource_server.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    bind = op.get_bind()
    admin_settings = AdminSettings()

    if admin_settings.admin_emails and admin_settings.admin_passwords:
        emails = admin_settings.admin_emails.split(",")
        passwords = admin_settings.admin_passwords.split(",")

        if len(emails) == len(passwords):
            user_table = sa.Table(
                "user",
                sa.MetaData(),
                sa.Column("id", sa.UUID()),
                sa.Column("email", sa.String()),
                sa.Column("is_email_confirmed", sa.Boolean()),
                sa.Column("hashed_password", sa.String()),
                sa.Column("avatar_path", sa.String()),
                sa.Column("is_admin", sa.Boolean()),
            )
            pwd_hasher = PasswordHasherImpl(PasswordHasher())
            admins = [
                {
                    "id": uuid4(),
                    "email": email.strip(),
                    "is_email_confirmed": True,
                    "hashed_password": pwd_hasher.hash_password(
                        RawPassword(password.strip())
                    ).value,
                    "is_admin": True,
                }
                for email, password in zip(emails, passwords, strict=False)
            ]

            bind.execute(user_table.insert(), admins)


def downgrade() -> None:
    # Удаляем администраторов перед удалением таблиц
    bind = op.get_bind()
    admin_settings = AdminSettings()

    if admin_settings.admin_emails:
        emails = [
            email.strip() for email in admin_settings.admin_emails.split(",")
        ]
        user_table = sa.Table(
            "user", sa.MetaData(), sa.Column("email", sa.String())
        )
        bind.execute(user_table.delete().where(user_table.c.email.in_(emails)))

    op.drop_table("user_role_association")
    op.drop_table("user_client_association")
    op.drop_table("role")
    op.drop_table("user")
    op.drop_table("client")
    op.drop_table("client_rs_association_table")
    op.drop_table("resource_server")
    op.drop_table("user_rs_association_table")
