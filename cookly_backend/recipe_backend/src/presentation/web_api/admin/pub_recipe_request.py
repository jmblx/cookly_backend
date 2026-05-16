import typing

from sqladmin import ModelView
from sqladmin.fields import SelectField

from domain.entities.value_objects import PubRecipeRequestStatus
from infrastructure.db.models import PubRecipeRequest


class PubRecipeRequestAdmin(ModelView, model=PubRecipeRequest):
    name = "Заявка на публикацию рецепта"
    name_plural = "Заявки на публикацию рецептов"

    column_list: typing.ClassVar = [
        PubRecipeRequest.id,
        PubRecipeRequest.status,
        PubRecipeRequest.reviewed_at,
        PubRecipeRequest.created_at,
        PubRecipeRequest.recipe_id,
        PubRecipeRequest.author_id,
        PubRecipeRequest.moderator_id,
    ]
    column_details_list: typing.ClassVar = [
        PubRecipeRequest.id,
        PubRecipeRequest.feedback,
        PubRecipeRequest.status,
        PubRecipeRequest.reviewed_at,
        PubRecipeRequest.created_at,
        PubRecipeRequest.recipe,
        PubRecipeRequest.author,
        PubRecipeRequest.moderator,
    ]

    form_overrides: typing.ClassVar = {
        "status": SelectField,
    }

    form_args: typing.ClassVar = {
        "status": {
            "choices": [(item.value, item.name) for item in PubRecipeRequestStatus],
            "coerce": str,
            "label": "Publication status",
        }
    }

    column_formatters: typing.ClassVar = {
        PubRecipeRequest.status: lambda m, a: PubRecipeRequestStatus(m.status).name if m.status else "-"
    }

    column_formatters_detail: typing.ClassVar = {
        PubRecipeRequest.status: lambda m, a: PubRecipeRequestStatus(m.status).name if m.status else "-"
    }

    column_sortable_list: typing.ClassVar = [
        PubRecipeRequest.id,
        PubRecipeRequest.status,
        PubRecipeRequest.created_at,
        PubRecipeRequest.reviewed_at,
    ]
