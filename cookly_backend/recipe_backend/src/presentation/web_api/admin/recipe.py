import typing

from sqladmin import ModelView
from sqladmin.fields import SelectField

from domain.entities.value_objects import MealTimeType
from infrastructure.db.models import Recipe


class RecipeAdmin(ModelView, model=Recipe):
    name = "Рецепт"
    name_plural = "Рецепты"

    column_list: typing.ClassVar = [
        Recipe.id,
        Recipe.title,
        Recipe.author_id,
        Recipe.estimated_time,
        Recipe.calories_by_100grams,
        Recipe.meal_time,
        Recipe.rating_sum,
        Recipe.rating_count,
        Recipe.is_public,
        Recipe.created_at,
    ]
    column_details_list: typing.ClassVar = [
        Recipe.id,
        Recipe.title,
        Recipe.description,
        Recipe.estimated_time,
        Recipe.calories_by_100grams,
        Recipe.meal_time,
        Recipe.rating_sum,
        Recipe.rating_count,
        Recipe.is_public,
        Recipe.created_at,
        Recipe.author,
        Recipe.steps,
        Recipe.pub_requests,
    ]
    form_columns: typing.ClassVar = [
        Recipe.id,
        Recipe.title,
        Recipe.description,
        Recipe.estimated_time,
        Recipe.calories_by_100grams,
        Recipe.meal_time,
        Recipe.rating_sum,
        Recipe.rating_count,
        Recipe.is_public,
        Recipe.created_at,
        Recipe.author,
    ]

    form_overrides: typing.ClassVar = {
        "meal_time": SelectField,
    }

    form_args: typing.ClassVar = {
        "meal_time": {
            "choices": [(item.value, item.name) for item in MealTimeType],
            "coerce": str,
            "label": "Meal time type"
        }
    }

    column_formatters: typing.ClassVar = {
        Recipe.meal_time: lambda m, a: MealTimeType(m.meal_time).name if m.meal_time else "-"
    }
