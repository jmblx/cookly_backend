import typing
import uuid
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from domain.entities.value_objects import RoleType
from infrastructure.db.models import Base, PubRecipeRequest
from infrastructure.db.models.common import added_at, intpk

if typing.TYPE_CHECKING:
    from infrastructure.db.models import CookingSession, IngredientGroup, Recipe, UserRecipe


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[added_at]
    role: Mapped[RoleType] = mapped_column(String(255), default=RoleType.user.value)

    created_recipes: Mapped[list["Recipe"]] = relationship("Recipe", back_populates="author")
    recipe_requests: Mapped[list["PubRecipeRequest"]] = relationship(
        "PubRecipeRequest",
        foreign_keys="PubRecipeRequest.author_id",
        back_populates="author",
    )
    recipe_requests_reviewed: Mapped[list["PubRecipeRequest"]] = relationship(
        "PubRecipeRequest",
        foreign_keys="PubRecipeRequest.moderator_id",
        back_populates="moderator",
    )
    cooking_sessions: Mapped[list["CookingSession"]] = relationship("CookingSession", back_populates="user")
    ingredient_groups: Mapped[list["IngredientGroup"]] = relationship(
        "IngredientGroup",
        secondary="user_ingredient_group"
    )
    user_recipes: Mapped[list["UserRecipe"]] = relationship("UserRecipe", back_populates="user")
    chief_chat: Mapped["UserChiefChat"] = relationship("UserChiefChat", back_populates="user")

    def __repr__(self):
        return f"<User {self.id}: {self.email}, {self.role}>"


class UserChiefChat(Base):
    __tablename__ = "user_chief_chat"

    id: Mapped[intpk]
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    chat_content: Mapped[dict] = mapped_column(JSONB())

    user: Mapped["User"] = relationship("User", back_populates="chief_chat")
