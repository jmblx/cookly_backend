import typing

from sqladmin import ModelView
from sqladmin.fields import SelectField

from domain.entities.value_objects import RoleType
from infrastructure.db.models import User


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"

    column_list: typing.ClassVar = [
        User.id,
        User.email,
        User.is_active,
        User.created_at,
    ]
    column_details_list: typing.ClassVar = [
        User.id,
        User.email,
        User.is_active,
        User.created_at,
        User.created_recipes,
        User.recipe_requests,
        User.recipe_requests_reviewed,
        User.ingredient_groups,
        User.user_recipes,
        User.chief_chat,
    ]
    form_columns: typing.ClassVar = [
        User.id,
        User.email,
        User.is_active,
        User.created_at,
        User.ingredient_groups,
    ]

    form_overrides: typing.ClassVar = {
        "role": SelectField,
    }

    form_args: typing.ClassVar = {
        "role": {
            "choices": [(item.value, item.name) for item in RoleType],
            "coerce": str,
            "label": "Role"
        }
    }

    column_formatters: typing.ClassVar = {
        User.role: lambda m, a: RoleType(m.meal_time).name if m.meal_time else "-"
    }
