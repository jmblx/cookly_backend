from pydantic import BaseModel


class IngredientGroupIds(BaseModel):
    ingredient_group_ids: list[int]
