from dishka import Provider, Scope, provide

from application.client.client_ref.common.repo import RefRepository
from application.client.common.client_repo import ClientRepository
from application.common.interfaces.role_repo import RoleRepository
from application.common.interfaces.user_repo import UserRepository
from application.resource_server.common.rs_repo import ResourceServerRepository
from infrastructure.db.repositories.client_ref_repo import RefRepositoryImpl
from infrastructure.db.repositories.client_repo_impl import (
    ClientRepositoryImpl,
)
from infrastructure.db.repositories.role_repository import RoleRepositoryImpl
from infrastructure.db.repositories.rs_repo_impl import (
    ResourceServerRepositoryImpl,
)
from infrastructure.db.repositories.user_repo_impl import UserRepositoryImpl


class RepositoriesProvider(Provider):
    user_repo = provide(
        UserRepositoryImpl, scope=Scope.REQUEST, provides=UserRepository
    )
    client_repo = provide(
        ClientRepositoryImpl, scope=Scope.REQUEST, provides=ClientRepository
    )
    role_repo = provide(
        RoleRepositoryImpl, scope=Scope.REQUEST, provides=RoleRepository
    )
    rs_repo = provide(
        ResourceServerRepositoryImpl,
        scope=Scope.REQUEST,
        provides=ResourceServerRepository,
    )
    ref_repo = provide(
        RefRepositoryImpl, scope=Scope.REQUEST, provides=RefRepository
    )
    # strategy_repo = provide(StrategyRepo, scope=Scope.REQUEST)
