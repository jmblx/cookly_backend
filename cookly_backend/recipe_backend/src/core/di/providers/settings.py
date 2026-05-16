from typing import NewType

from dishka import Provider, Scope, provide

from core.config import (
    AppConfig,
    AuthCoreConfig,
    DatabaseConfig,
    GlobalConfig,
    GunicornConfig,
    JWTConfig,
    MinioConfig,
    OllamaConfig,
    RedisConfig,
    config_loader,
)

LoggingConfig = NewType("LoggingConfig", dict)


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_app_config(self) -> AppConfig:
        return config_loader.app_config

    @provide
    def provide_gunicorn_config(self) -> GunicornConfig:
        return config_loader.app_config.gunicorn

    @provide
    def provide_db_config(self) -> DatabaseConfig:
        config = config_loader.app_config.database
        config.db_uri = f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"
        return config

    @provide
    def provide_redis_config(self) -> RedisConfig:
        config = config_loader.app_config.redis
        config.uri = f"redis://{config.host}:{config.port}"
        return config

    @provide
    def provide_global_config(self) -> GlobalConfig:
        return config_loader.app_config.global_

    @provide
    def provide_logging_config(self) -> LoggingConfig:
        return config_loader.logging_config

    @provide(scope=Scope.APP, provides=JWTConfig)
    def provide_jwt_config(self) -> JWTConfig:
        return config_loader.app_config.jwt

    @provide(scope=Scope.APP, provides=AuthCoreConfig)
    def provide_auth_core_config(self) -> AuthCoreConfig:
        return config_loader.app_config.auth_core

    @provide(scope=Scope.APP, provides=MinioConfig)
    def provide_minio_config(self) -> MinioConfig:
        return config_loader.app_config.minio

    @provide(scope=Scope.APP, provides=OllamaConfig)
    def provide_ollama_config(self) -> OllamaConfig:
        return config_loader.app_config.ollama
