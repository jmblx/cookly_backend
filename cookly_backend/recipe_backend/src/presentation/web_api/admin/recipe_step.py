import typing

from sqladmin import ModelView

from infrastructure.db.models.recipe import RecipeStep


class RecipeStepAdmin(ModelView, model=RecipeStep):
    name = "Шаг рецептов"
    name_plural = "Шаги рецептов"

    column_list: typing.ClassVar = [
        RecipeStep.id,
        RecipeStep.title,
        RecipeStep.number,
        RecipeStep.recipe_id,
    ]
    column_details_list: typing.ClassVar = [
        RecipeStep.id,
        RecipeStep.title,
        RecipeStep.description,
        RecipeStep.number,
        RecipeStep.recipe,
    ]
