import typing

from sqladmin import ModelView

from infrastructure.db.models import RecipeCategory


class RecipeCategoryAdmin(ModelView, model=RecipeCategory):
    name = "Категория рецептов"
    name_plural = "Категории рецептов"

    column_list: typing.ClassVar = [
        RecipeCategory.id,
        RecipeCategory.title,
    ]

    column_details_list: typing.ClassVar = [
        RecipeCategory.id,
        RecipeCategory.title,
        RecipeCategory.recipes,
    ]

    form_excluded_columns: typing.ClassVar = [
        RecipeCategory.search_vector,
    ]
