"""empty message

Revision ID: 9d7990301a72
Revises: 114bc5d09afd
Create Date: 2026-04-26 14:13:28.383987

"""
import csv
import os
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d7990301a72'
down_revision: Union[str, None] = '114bc5d09afd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _read_csv(file_path: str, columns: list[str]):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append({col: row[col] for col in columns})
        return rows


def upgrade():
    base_path = os.environ.get("CSV_SEED_DIR")
    if not base_path:
        raise RuntimeError("CSV_SEED_DIR is not set")

    # --- ingredient ---
    ingredient_table = sa.table(
        "ingredient",
        sa.column("title", sa.String),
        sa.column("default_unit_measurement", sa.String),
    )

    ingredient_rows = _read_csv(
        os.path.join(base_path, "ingredient.csv"),
        ["title", "default_unit_measurement"],
    )

    op.bulk_insert(ingredient_table, ingredient_rows)

    # --- ingredient_group ---
    ingredient_group_table = sa.table(
        "ingredient_group",
        sa.column("title", sa.String),
    )

    ingredient_group_rows = _read_csv(
        os.path.join(base_path, "ingredient_group.csv"),
        ["title"],
    )

    op.bulk_insert(ingredient_group_table, ingredient_group_rows)

    # --- recipe_category ---
    recipe_category_table = sa.table(
        "recipe_category",
        sa.column("title", sa.String),
    )

    recipe_category_rows = _read_csv(
        os.path.join(base_path, "recipe_category.csv"),
        ["title"],
    )

    op.bulk_insert(recipe_category_table, recipe_category_rows)


def downgrade():
    # op.execute("DELETE FROM recipe_category")
    # op.execute("DELETE FROM ingredient_group")
    # op.execute("DELETE FROM ingredient")
    ...
