from abc import ABC, abstractmethod
from typing import NewType, TypedDict


class SetAvatarResponse(TypedDict, total=False):
    avatar_update_timestamp: int
    avatar_presigned_url: str


class StorageService(ABC):
    @abstractmethod
    async def set_avatar(
        self, content: bytes, content_type: str, object_id: str
    ) -> SetAvatarResponse:
        """
        Загружает файл в указанный бакет.

        :param bucket_name: Название бакета
        :param filename: Имя файла в бакете
        :param content: Содержимое файла в байтах
        :param content_type: MIME-тип содержимого файла
        :param object_id: тот кому принадлежит аватар новый
        :return: URL загруженного файла
        """

    @abstractmethod
    def get_presigned_avatar_url(self, filename: str) -> str:
        """
        Возвращает подписанную ссылку на файл в бакете.

        :param filename: Имя файла в бакете без расширения (id объекта в виде строки)
        :return: Подписанная ссылка на файл
        """


class UserS3StorageService(StorageService):
    @abstractmethod
    async def get_user_avatar_update_timestamp(
        self, user_id: str
    ) -> int | None: ...


ClientS3StorageService = NewType("ClientS3StorageService", StorageService)
