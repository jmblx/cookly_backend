from dishka import Provider, from_context, provide, Scope

from src.application.email_notification.email_confirmation.handler import EmailConfirmationHandler
from src.application.email_notification.reset_password.handler import ResetPasswordHandler
from src.application.email_notification.smtp_service import SmtpService
from src.application.email_notification.third_party_register_notify.handler import ThirdPartyRegisterHandler
from src.config import Config, SmtpConfig, NatsConfig, ApiPathsConfig


class AppProvider(Provider):
    smtp_service = provide(SmtpService, scope=Scope.REQUEST)
    email_confirmation_handler = provide(EmailConfirmationHandler, scope=Scope.REQUEST)
    reset_password_handler = provide(ResetPasswordHandler, scope=Scope.REQUEST)
    third_party_email_confirmation_handler = provide(ThirdPartyRegisterHandler, scope=Scope.REQUEST)


class ConfigProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def smtp_conf(self, config: Config) -> SmtpConfig:
        return config.smtp

    @provide(scope=Scope.APP)
    def nats_conf(self, config: Config) -> NatsConfig:
        return config.nats

    @provide(scope=Scope.APP)
    def api_paths_conf(self, config: Config) -> ApiPathsConfig:
        return config.api_paths
