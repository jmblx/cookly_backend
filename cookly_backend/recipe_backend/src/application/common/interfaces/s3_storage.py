from abc import ABC, abstractmethod


class S3Storage(ABC):
    """Абстрактный интерфейс для S3-совместимого хранилища"""

    @abstractmethod
    async def set_recipe_image(self, content: bytes, object_id: str) -> str:
        """Сохраняет изображение рецепта, возвращает URL"""

    @abstractmethod
    async def set_recipe_step_image(self, content: bytes, object_id: str) -> str:
        """Сохраняет изображение шага рецепта, возвращает URL"""
