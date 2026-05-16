import os

import argon2
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from application.auth_as.common.scopes_service import ScopesService
from application.common.id_provider import (
    ClientIdentityProvider,
    ClientIdentityProviderImpl,
    UserIdentityProvider,
    UserIdentityProviderImpl,
)
from application.common.interfaces.auth_server_token_creation import (
    AuthServerTokenCreationService,
)
from application.common.interfaces.client_token_creation import (
    ClientTokenCreationService,
)
from application.common.interfaces.email_confirmation_service import (
    EmailConfirmationServiceI,
)
from application.common.interfaces.http_auth import (
    HttpAuthServerService,
    HttpClientService,
)
from application.common.interfaces.imedia_storage import (
    ClientS3StorageService,
    UserS3StorageService,
)
from application.common.interfaces.jwt_service import JWTService
from application.common.interfaces.notify_service import NotifyService
from application.common.interfaces.white_list import (
    AuthServerTokenWhitelistService,
    ClientTokenWhitelistService,
)
from application.common.services.auth_code import AuthorizationCodeStorage
from application.common.services.client_service import ClientService
from application.common.services.pkce import PKCEService
from application.third_party_auth.common.third_party_notification_service import (
    ThirdPartyNotificationService,
)
from application.third_party_auth.yandex.idp import YandexIdentityProvider
from application.user.reset_pwd.service import ResetPwdService
from domain.common.services.pwd_service import PasswordHasher
from infrastructure.external_services.message_routing.notify_service import (
    NotifyServiceImpl,
)
from infrastructure.external_services.storage.config import MinIOConfig
from infrastructure.external_services.storage.minio_service import (
    MinIOService,
    UserMinIOService,
)
from infrastructure.services.auth.auth_code import (
    RedisAuthorizationCodeStorage,
)
from infrastructure.services.auth.auth_server_token_creation import (
    AuthServerTokenCreationServiceImpl,
)
from infrastructure.services.auth.client_auth_service import (
    HttpClientServiceImpl,
)
from infrastructure.services.auth.client_token_creation import (
    ClientTokenCreationServiceImpl,
)
from infrastructure.services.auth.jwt_service import JWTServiceImpl
from infrastructure.services.auth.reset_pwd_service import ResetPwdServiceImpl
from infrastructure.services.auth.scopes_service import ScopesServiceImpl
from infrastructure.services.auth.user_auth_server_service import (
    HttpAuthServerServiceImpl,
)
from infrastructure.services.auth.white_list_service import (
    AuthServerTokenWhitelistServiceImpl,
    ClientTokenWhitelistServiceImpl,
)
from infrastructure.services.notification.email_confirmation_service import (
    EmailConfirmationService,
)
from infrastructure.services.notification.third_party_notification_service import (
    ThirdPartyNotificationServiceImpl,
)
from infrastructure.services.security.pwd_service import PasswordHasherImpl


class ServiceProvider(Provider):

    # @provide(scope=Scope.REQUEST, provides=UserService)
    # def provide_user_service(
    #     self, user_repo: UserRepository
    # ) -> UserService:
    #     return UserServiceImpl(user_repo)
    # storage_service = provide(
    #     MinIOService, scope=Scope.REQUEST, provides=StorageService
    # )
    @provide(scope=Scope.APP, provides=PasswordHasher)
    def provide_ph(self) -> PasswordHasher:
        return PasswordHasherImpl(argon2.PasswordHasher())

    pkce_service = provide(PKCEService, scope=Scope.APP)
    auth_code_service = provide(
        RedisAuthorizationCodeStorage,
        scope=Scope.REQUEST,
        provides=AuthorizationCodeStorage,
    )
    jwt_service = provide(
        JWTServiceImpl, scope=Scope.REQUEST, provides=JWTService
    )
    http_auth_server_service = provide(
        HttpAuthServerServiceImpl,
        scope=Scope.REQUEST,
        provides=HttpAuthServerService,
    )
    token_creation_service = provide(
        AuthServerTokenCreationServiceImpl,
        scope=Scope.REQUEST,
        provides=AuthServerTokenCreationService,
    )
    client_token_creation_service = provide(
        ClientTokenCreationServiceImpl,
        scope=Scope.REQUEST,
        provides=ClientTokenCreationService,
    )
    # token_white_list_service = provide(
    #     TokenWhiteListServiceImpl,
    #     scope=Scope.REQUEST,
    #     provides=TokenWhiteListService,
    # )
    client_service = provide(ClientService, scope=Scope.REQUEST)
    user_identity_provider = provide(
        UserIdentityProviderImpl,
        scope=Scope.REQUEST,
        provides=UserIdentityProvider,
    )
    client_identity_provider = provide(
        ClientIdentityProviderImpl,
        scope=Scope.REQUEST,
        provides=ClientIdentityProvider,
    )
    # investment_service = provide(InvestmentsService, scope=Scope.REQUEST)
    notify_service = provide(
        NotifyServiceImpl, scope=Scope.REQUEST, provides=NotifyService
    )
    email_confirmation_service = provide(
        EmailConfirmationService,
        scope=Scope.REQUEST,
        provides=EmailConfirmationServiceI,
    )
    reset_pwd_service = provide(
        ResetPwdServiceImpl, scope=Scope.REQUEST, provides=ResetPwdService
    )
    # user_service = provide(
    #     UserServiceImpl, scope=Scope.REQUEST, provides=UserService
    # )
    scopes_service = provide(
        ScopesServiceImpl, scope=Scope.REQUEST, provides=ScopesService
    )
    http_client_service = provide(
        HttpClientServiceImpl, scope=Scope.REQUEST, provides=HttpClientService
    )
    client_token_service = provide(
        ClientTokenWhitelistServiceImpl,
        scope=Scope.REQUEST,
        provides=ClientTokenWhitelistService,
    )
    auth_server_token_service = provide(
        AuthServerTokenWhitelistServiceImpl,
        scope=Scope.REQUEST,
        provides=AuthServerTokenWhitelistService,
    )
    oauth_identity_provider = provide(
        YandexIdentityProvider,
        scope=Scope.REQUEST,
        provides=YandexIdentityProvider,
    )
    third_party_notification_service = provide(
        ThirdPartyNotificationServiceImpl,
        scope=Scope.REQUEST,
        provides=ThirdPartyNotificationService,
    )

    @provide(scope=Scope.REQUEST, provides=UserS3StorageService)
    def provide_user_minio_service(
        self, config: MinIOConfig, redis: Redis
    ) -> UserS3StorageService:
        return UserMinIOService(
            config,
            bucket_name=os.getenv("MINIO_USER_AVATAR_BUCKET_NAME"),
            redis=redis,
        )

    @provide(scope=Scope.REQUEST, provides=ClientS3StorageService)
    def provide_client_minio_service(
        self, config: MinIOConfig, redis: Redis
    ) -> ClientS3StorageService:
        return MinIOService(
            config, bucket_name=os.getenv("MINIO_CLIENT_AVATAR_BUCKET_NAME")
        )

    # reg_validation_service = provide(
    #     RegUserValidationService,
    #     scope=Scope.REQUEST,
    #     provides=UserValidationService,
    # )
