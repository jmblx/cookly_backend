from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo


class PubRecipeRequestStatus(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MealTimeType(Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    supper = "supper"


class CookingSessionStatus(Enum):
    active = "active"
    finished = "finished"
    cancelled = "cancelled"


def get_current_meal_time(tz: ZoneInfo) -> MealTimeType:
    """
    Определяет текущее время приёма пищи на основе времени суток.

    Args:
        tz (ZoneInfo): Часовой пояс пользователя

    Returns:
        MealTimeType: Текущее время приёма пищи

    Примеры:
        - 06:00 - 11:59 → breakfast
        - 12:00 - 17:59 → lunch
        - 18:00 - 05:59 → supper
    """
    current_time = datetime.now(tz).time()

    breakfast_start = 6  # 6:00
    breakfast_end = 12  # 11:59
    lunch_start = 12  # 12:00
    lunch_end = 18  # 17:59

    if breakfast_start <= current_time.hour < breakfast_end:
        return MealTimeType.breakfast
    elif lunch_start <= current_time.hour < lunch_end:
        return MealTimeType.lunch
    else:
        return MealTimeType.supper


class RoleType(Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


RECIPE_MODERATOR_ROLES = frozenset([RoleType.admin.value, RoleType.moderator.value])
