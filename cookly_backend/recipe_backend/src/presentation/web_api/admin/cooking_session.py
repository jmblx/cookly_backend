import typing

from sqladmin import ModelView

from infrastructure.db.models import CookingSession


class CookingSessionAdmin(ModelView, model=CookingSession):
    name = "Сессия приготовления"
    name_plural = "Сессия приготовления"

    column_list: typing.ClassVar = [
        CookingSession.id,
        CookingSession.last_activity,
        CookingSession.current_step,
        CookingSession.start_time,
        CookingSession.end_time,
        CookingSession.status,
        CookingSession.user_id,
        CookingSession.recipe_id,
    ]

    column_details_list: typing.ClassVar = [
        CookingSession.id,
        CookingSession.last_activity,
        CookingSession.current_step,
        CookingSession.start_time,
        CookingSession.end_time,
        CookingSession.status,
        CookingSession.user,
        CookingSession.recipe,
    ]
