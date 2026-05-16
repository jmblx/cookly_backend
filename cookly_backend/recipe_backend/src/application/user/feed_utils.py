from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import String, and_, case, cast, exists, func, literal, or_

from application.user.common.preference_service import (
    UserPreferenceProfile,
    build_category_preference_score,
    build_difficulty_preference_score,
    build_spicy_preference_score,
)
from infrastructure.db.models import Recipe


@dataclass
class ScoreConfig:
    rating_weight: float = 0.45
    meal_weight: float = 0.2
    random_weight: float = 0.1

    difficulty_weight: float = 0.10
    spicy_weight: float = 0.05
    category_weight: float = 0.10

    strict_meal: bool = False


def build_rating_score():
    rating_score = (
        (Recipe.rating_sum + 10 * 3.5) /
        (Recipe.rating_count + 10)
    )
    return rating_score / 2.0


def build_meal_score(meal_time: str, *, strict: bool = False):
    if strict:
        return None

    return case(
        (Recipe.meal_time == meal_time, 1.0),
        else_=0.3
    )


def build_random_score(user_id: UUID, seed: str):
    return (
        func.abs(
            func.hashtext(
                cast(Recipe.id, String)
                + literal("_")
                + literal(str(user_id))
                + literal("_")
                + literal(seed)
            )
        ) % 1000
    ) / 1000.0


def build_total_score(
    config: ScoreConfig,
    user_id: UUID,
    meal_time: str,
    seed: str,
    preferences: UserPreferenceProfile | None,
):
    rating_score = build_rating_score()

    meal = build_meal_score(meal_time, strict=config.strict_meal)
    random_score = build_random_score(user_id, seed)

    difficulty_score = (
        build_difficulty_preference_score(preferences)
    )

    spicy_score = (
        build_spicy_preference_score(preferences)
    )

    category_score = (
        build_category_preference_score(preferences)
    )

    score = (
        rating_score * config.rating_weight +
        random_score * config.random_weight +
        difficulty_score * config.difficulty_weight +
        spicy_score * config.spicy_weight +
        category_score * config.category_weight
    )

    if meal is not None:
        score += meal * config.meal_weight

    return score


def apply_base_filters(stmt, user_id, excluded_subq):
    return stmt.where(
        Recipe.is_public == True, # noqa: E712
        Recipe.author_id != user_id,
        ~exists(excluded_subq)
    )


def apply_meal_filter(stmt, meal_time: str, *, strict: bool):
    if strict:
        return stmt.where(Recipe.meal_time == meal_time)
    return stmt


def apply_keyset_pagination(stmt, score, last_score, last_id):
    if last_score is None or last_id is None:
        return stmt

    return stmt.where(
        or_(
            score < last_score,
            and_(
                score == last_score,
                Recipe.id < last_id
            )
        )
    )
