"""empty message

Revision ID: 5a438817a005
Revises: ff158c3bc536
Create Date: 2026-05-02 15:39:52.073978

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a438817a005'
down_revision: Union[str, None] = 'ff158c3bc536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# В миграции Alembic

def upgrade():
    # Добавляем колонку search_vector
    op.add_column('recipe',
                  sa.Column('search_vector', postgresql.TSVECTOR())
                  )

    # Создаем индексы
    op.create_index(
        'ix_recipe_search_vector',
        'recipe',
        ['search_vector'],
        postgresql_using='gin'
    )
    op.create_index(
        'ix_recipe_title_trgm',
        'recipe',
        ['title'],
        postgresql_using='gin',
        postgresql_ops={'title': 'gin_trgm_ops'}
    )

    # Триггерная функция обновления search_vector
    op.execute("""
    CREATE OR REPLACE FUNCTION recipe_search_vector_update()
    RETURNS trigger AS $$
    BEGIN
        NEW.search_vector :=
            -- Приоритет 1: название + описание рецепта (вес A)
            setweight(to_tsvector('russian', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('russian', coalesce(NEW.description, '')), 'A') ||

            -- Приоритет 2: категории (вес B)
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(rc.title, ' ')
                FROM recipe_category rc
                JOIN recipe_recipe_category rrc ON rrc.recipe_category_id = rc.id
                WHERE rrc.recipe_id = NEW.id
            ), '')), 'B') ||

            -- Приоритет 3: ингредиенты (вес C)
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(i.title || ' ' || coalesce(ig.title, ''), ' ')
                FROM ingredient i
                JOIN recipe_ingredient ri ON ri.ingredient_id = i.id
                LEFT JOIN ingredient_ingredient_group iig ON iig.ingredient_id = i.id
                LEFT JOIN ingredient_group ig ON ig.id = iig.ingredient_group_id
                WHERE ri.recipe_id = NEW.id
            ), '')), 'C') ||

            -- Приоритет 4: шаги (вес D)
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(rs.title || ' ' || coalesce(rs.description, ''), ' ')
                FROM recipe_step rs
                WHERE rs.recipe_id = NEW.id
            ), '')), 'D');

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Триггер на INSERT/UPDATE рецепта
    op.execute("""
    CREATE TRIGGER trg_recipe_search_vector
    BEFORE INSERT OR UPDATE ON recipe
    FOR EACH ROW
    EXECUTE FUNCTION recipe_search_vector_update();
    """)

    # Триггеры на изменение связанных таблиц
    op.execute("""
    CREATE OR REPLACE FUNCTION recipe_search_vector_refresh()
    RETURNS trigger AS $$
    DECLARE
        recipe_id int;
    BEGIN
        IF TG_TABLE_NAME = 'recipe_ingredient' THEN
            recipe_id := COALESCE(NEW.recipe_id, OLD.recipe_id);
        ELSIF TG_TABLE_NAME = 'recipe_recipe_category' THEN
            recipe_id := COALESCE(NEW.recipe_id, OLD.recipe_id);
        ELSIF TG_TABLE_NAME = 'recipe_step' THEN
            recipe_id := COALESCE(NEW.recipe_id, OLD.recipe_id);
        END IF;

        UPDATE recipe 
        SET search_vector = (
            SELECT 
                setweight(to_tsvector('russian', coalesce(r.title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(r.description, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce((
                    SELECT string_agg(rc.title, ' ')
                    FROM recipe_category rc
                    JOIN recipe_recipe_category rrc ON rrc.recipe_category_id = rc.id
                    WHERE rrc.recipe_id = r.id
                ), '')), 'B') ||
                setweight(to_tsvector('russian', coalesce((
                    SELECT string_agg(i.title || ' ' || coalesce(ig.title, ''), ' ')
                    FROM ingredient i
                    JOIN recipe_ingredient ri ON ri.ingredient_id = i.id
                    LEFT JOIN ingredient_ingredient_group iig ON iig.ingredient_id = i.id
                    LEFT JOIN ingredient_group ig ON ig.id = iig.ingredient_group_id
                    WHERE ri.recipe_id = r.id
                ), '')), 'C') ||
                setweight(to_tsvector('russian', coalesce((
                    SELECT string_agg(rs.title || ' ' || coalesce(rs.description, ''), ' ')
                    FROM recipe_step rs
                    WHERE rs.recipe_id = r.id
                ), '')), 'D')
            FROM recipe r
            WHERE r.id = recipe_id
        )
        WHERE id = recipe_id;

        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Триггеры на изменение связанных данных
    for table in ['recipe_ingredient', 'recipe_recipe_category', 'recipe_step']:
        op.execute(f"""
        CREATE TRIGGER trg_{table}_recipe_search_refresh
        AFTER INSERT OR UPDATE OR DELETE ON {table}
        FOR EACH ROW
        EXECUTE FUNCTION recipe_search_vector_refresh();
        """)

    # Первоначальное заполнение search_vector
    op.execute("""
    UPDATE recipe r SET search_vector = (
        SELECT 
            setweight(to_tsvector('russian', coalesce(r.title, '')), 'A') ||
            setweight(to_tsvector('russian', coalesce(r.description, '')), 'B') ||
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(rc.title, ' ')
                FROM recipe_category rc
                JOIN recipe_recipe_category rrc ON rrc.recipe_category_id = rc.id
                WHERE rrc.recipe_id = r.id
            ), '')), 'B') ||
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(i.title || ' ' || coalesce(ig.title, ''), ' ')
                FROM ingredient i
                JOIN recipe_ingredient ri ON ri.ingredient_id = i.id
                LEFT JOIN ingredient_ingredient_group iig ON iig.ingredient_id = i.id
                LEFT JOIN ingredient_group ig ON ig.id = iig.ingredient_group_id
                WHERE ri.recipe_id = r.id
            ), '')), 'C') ||
            setweight(to_tsvector('russian', coalesce((
                SELECT string_agg(rs.title || ' ' || coalesce(rs.description, ''), ' ')
                FROM recipe_step rs
                WHERE rs.recipe_id = r.id
            ), '')), 'D')
    );
    """)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
