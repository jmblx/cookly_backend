from dataclasses import dataclass
from typing import NewType

from domain.exceptions.role import InvalidPermissionsError

# @dataclass(frozen=True)
# class RoleID:
#     value: int

RoleID = NewType("RoleID", int)


@dataclass(frozen=True)
class RoleName:
    value: str


@dataclass(frozen=True)
class RoleBaseScopes:
    value: dict[str, int]

    @classmethod
    def create(cls, value_dict: dict[str, str]) -> "RoleBaseScopes":
        """
        Создает объект RoleBaseScopes из словаря, где значения - строки побитовых чисел.
        Преобразует строки в целые числа.
        """
        new_value = {}
        for key, permission_str in value_dict.items():
            if (
                not isinstance(permission_str, str)
                or len(permission_str) != 4
                or not all(c in "01" for c in permission_str)
            ):
                raise InvalidPermissionsError(
                    f"Permission value for key '{key}' must be a 4-bit binary string."
                )
            permission_int = int(permission_str, 2)
            new_value[key] = permission_int
        return cls(new_value)

    def __post_init__(self) -> None:
        """
        Проверка валидности значений в словаре.
        Убедитесь, что все значения - целые числа от 0 до 15.
        """
        for key, permission in self.value.items():
            if not isinstance(key, str):
                raise TypeError(f"Key {key} must be a string")
            if not isinstance(permission, int) or not self._is_valid_bitwise(
                permission
            ):
                raise InvalidPermissionsError(
                    f"Permission value {permission} for key '{key}' is not a valid 4-bit number"
                )

    @staticmethod
    def _is_valid_bitwise(value: int) -> bool:
        """
        Проверяет, является ли число 4-значным побитовым числом (0-15).
        """
        return 0 <= value <= 15

    def get_permission(self, key: str) -> int:
        """
        Получает значение разрешения по ключу.
        """
        return self.value.get(key, 0)

    def set_permission(self, key: str, permission: int) -> "RoleBaseScopes":
        """
        Устанавливает разрешение по ключу.
        Возвращает новый объект с обновленным значением разрешения.
        """
        if not self._is_valid_bitwise(permission):
            raise InvalidPermissionsError(
                f"Permission value {permission} is not a valid 4-bit number"
            )
        new_permissions = dict(self.value)
        new_permissions[key] = permission
        return RoleBaseScopes(new_permissions)

    def add_permission(
        self, key: str, permission_str: str
    ) -> "RoleBaseScopes":
        """
        Добавляет разрешение по ключу. Если в аргументе передается 1 в строке,
        то соответствующие биты в текущем значении заменяются на 1.
        """
        if len(permission_str) != 4 or not all(
            c in "01" for c in permission_str
        ):
            raise InvalidPermissionsError(
                "Permission string must be a 4-bit binary string."
            )

        permission_to_add = int(permission_str, 2)
        current_permission = self.get_permission(key)
        new_permission = current_permission | permission_to_add
        return self.set_permission(key, new_permission)

    def remove_permission(
        self, key: str, permission_str: str
    ) -> "RoleBaseScopes":
        """
        Убирает разрешение по ключу. Если в аргументе передается 1 в строке,
        то соответствующие биты в текущем значении заменяются на 0.
        """
        if len(permission_str) != 4 or not all(
            c in "01" for c in permission_str
        ):
            raise InvalidPermissionsError(
                "Permission string must be a 4-bit binary string."
            )

        permission_to_remove = int(permission_str, 2)
        current_permission = self.get_permission(key)
        new_permission = current_permission & ~permission_to_remove
        return self.set_permission(key, new_permission)

    def has_permission(self, key: str, bit: int) -> bool:
        """
        Проверяет, установлен ли определенный бит в значении разрешения по ключу.
        """
        if key not in self.value:
            return False
        return (self.value[key] & (1 << bit)) != 0

    def to_dict(self) -> dict[str, int]:
        """
        Возвращает словарь разрешений.
        """
        return self.value

    def to_list(self) -> list[str]:
        return [
            f"{scope}:{bitmask:04b}" for scope, bitmask in self.value.items()
        ]
