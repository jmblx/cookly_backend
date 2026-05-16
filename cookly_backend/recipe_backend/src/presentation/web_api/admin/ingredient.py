import typing

from sqladmin import ModelView

from infrastructure.db.models import Ingredient


class IngredientAdmin(ModelView, model=Ingredient):
    name = "Ингредиент"
    name_plural = "Ингредиенты"

    column_list: typing.ClassVar = [
        Ingredient.id,
        Ingredient.title,
        Ingredient.default_unit_measurement,
        Ingredient.created_at,
    ]
    form_excluded_columns: typing.ClassVar = [
        Ingredient.search_vector,
        Ingredient.ingredient_recipes
    ]
    column_details_list: typing.ClassVar = [
        Ingredient.id,
        Ingredient.title,
        Ingredient.default_unit_measurement,
        Ingredient.created_at,
        Ingredient.ingredient_groups,
    ]
