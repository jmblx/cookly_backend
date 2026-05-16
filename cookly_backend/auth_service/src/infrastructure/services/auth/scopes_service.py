from collections import defaultdict

from application.auth_as.common.scopes_service import ScopesService
from domain.entities.resource_server.value_objects import ResourceServerID
from domain.entities.role.model import Role


class ScopesServiceImpl(ScopesService):
    def calculate_full_user_scopes_for_client(
        self, roles_by_rs: dict[ResourceServerID, list[Role] | list[dict]]
    ) -> list[str]:
        """
        Вычисляет полный список разрешений в формате "rs_id:scope:bitmask".
        Объединяет битовые маски для одинаковых scope в рамках одного RS.
        """
        scopes = []

        for rs_id, roles in roles_by_rs.items():
            merged_permissions = defaultdict(int)

            for role in roles:
                base_scopes = (
                    role.base_scopes.value
                    if isinstance(role, Role)
                    else role["base_scopes"]
                )
                for scope, bitmask in base_scopes.items():
                    merged_permissions[scope] |= bitmask

            scopes.extend(
                f"{rs_id}:{scope}:{bitmask:04b}"
                for scope, bitmask in merged_permissions.items()
            )

        return scopes
