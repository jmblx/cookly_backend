from dishka import Provider, Scope, provide

from application.auth_as.get_available_accounts_query import (
    GetAvailableAccountsHandler,
)

# from application.bold_code.old_code_to_token_handler import (
#     CodeToTokenHandler,
# )
from application.auth_as.identify_by_cookies_query import (
    IdentifyByCookiesQueryHandler,
)
from application.auth_as.invalidate_other_tokens_handler import (
    InvalidateOtherTokensHandler,
)
from application.auth_as.login_user_auth_server import LoginUserHandler
from application.auth_as.refresh_tokens_auth_server_handler import (
    RefreshTokensHandler,
)
from application.auth_as.register_user_auth_server.confirm_registration_handler import CompleteRegisterUserHandler
from application.auth_as.register_user_auth_server.init_registration_hander import (
    InitRegisterUserHandler,
)
from application.auth_as.revoke_token_handler import (
    RevokeTokenHandler,
)
from application.auth_for_client.code_to_token_handler import (
    CodeToTokenHandler,
)
from application.auth_for_client.get_me_page_data_handler import (
    GetMeDataHandler,
)
from application.auth_for_client.get_userinfo_handler import (
    GetUserInfoQueryHandler,
)
from application.auth_for_client.refresh_tokens_handler import (
    RefreshClientTokensHandler,
)
from application.auth_for_client.revoke_token_handler import (
    RevokeClientTokenHandler,
)
from application.client.add_allowed_url import (
    AddAllowedRedirectUrlCommandHandler,
)
from application.client.avatar_query import GetClientAvatarHandler
from application.client.client_queries import (
    ClientAuthValidationQueryHandler,
)
from application.client.client_ref.create_ref_handler import RegisterRefHandler
from application.client.client_ref.read_ref_view_data_handler import ReadRefPageViewQueryHandler
from application.client.client_ref.update_ref_handler import UpdateRefCommandHandler
from application.client.find_clients import FindClientsHandler
from application.client.get_all_clients import GetClientsIdsHandler
from application.client.read_client_view_handler import (
    ReadClientPageViewQueryHandler,
)
from application.client.register_client_hadler import (
    RegisterClientHandler,
)
from application.client.set_client_avatar_handler import SetClientAvatarHandler
from application.client.update_client import (
    UpdateClientCommandHandler,
)
from application.resource_server.find_rs import FindRSHandler
from application.resource_server.get_all_resource_servers import (
    GetAllRSIdsHandler,
)
from application.resource_server.read_rs_view_handler import (
    ReadResourceServerPageViewQueryHandler,
)
from application.resource_server.register_rs_handler import (
    RegisterResourceServerHandler,
)
from application.resource_server.update_rs_handler import (
    UpdateResourceServerHandler,
)
from application.role.create_role_handler import CreateRoleHandler
from application.role.delete_role_handler import DeleteRoleHandler
from application.role.upd_role_command_handler import UpdateRoleHandler
from application.third_party_auth.yandex.login_handler import (
    YandexLoginHandler,
)
from application.third_party_auth.yandex.register_handler import (
    YandexRegisterHandler,
)
from application.user.add_role_to_user_handler import AddRoleToUserHandler
from application.user.confirm_email_handler import ConfirmEmailHandler
from application.user.delete_user_handler import DeleteUserHandler
from application.user.reset_pwd.request_change_pwd_handler import (
    RequestChangePasswordHandler,
)
from application.user.reset_pwd.reset_pwd_with_token import (
    ResetPasswordWithTokenHandler,
)
from application.user.reset_pwd.verify_reset_code_handler import (
    VerifyResetCodeHandler,
)
from application.user.set_user_avatar_handler import SetUserAvatarHandler


class HandlerProvider(Provider):
    reg_client_handler = provide(
        RegisterClientHandler,
        scope=Scope.REQUEST,
    )
    reg_user_handler = provide(
        InitRegisterUserHandler,
        scope=Scope.REQUEST,
    )
    complete_reg_user_handler = provide(CompleteRegisterUserHandler, scope=Scope.REQUEST)
    code_to_token_handler = provide(CodeToTokenHandler, scope=Scope.REQUEST)
    login_handler = provide(LoginUserHandler, scope=Scope.REQUEST)
    create_role_handler = provide(CreateRoleHandler, scope=Scope.REQUEST)
    update_role_handler = provide(UpdateRoleHandler, scope=Scope.REQUEST)
    revoke_tokens_handler = provide(RevokeTokenHandler, scope=Scope.REQUEST)
    refresh_tokens_handler = provide(RefreshTokensHandler, scope=Scope.REQUEST)
    client_auth_validation_query_handler = provide(
        ClientAuthValidationQueryHandler, scope=Scope.REQUEST
    )
    rename_client_command_handler = provide(
        UpdateClientCommandHandler, scope=Scope.REQUEST
    )
    add_allowed_redirect_url_command_handler = provide(
        AddAllowedRedirectUrlCommandHandler, scope=Scope.REQUEST
    )
    # get_investments_query_handler = provide(
    #     InvestmentsQueryHandler, scope=Scope.REQUEST
    # )
    # create_new_strategy_handler = provide(
    #     CreateNewStrategyHanlder, scope=Scope.REQUEST
    # )
    # read_strategy_handler = provide(StrategyQueryHandler, scope=Scope.REQUEST)
    # sell_investment_handler = provide(
    #     SellInvestmentHandler, scope=Scope.REQUEST
    # )
    # buy_investment_handler = provide(BuyInvestmentHandler, scope=Scope.REQUEST)
    # notification_query_handler = provide(
    #     NotificationQueryHandler, scope=Scope.REQUEST
    # )
    invalidate_tokens_exc_cur_handler = provide(
        InvalidateOtherTokensHandler, scope=Scope.REQUEST
    )
    confirm_email_handler = provide(ConfirmEmailHandler, scope=Scope.REQUEST)
    request_change_password_handler = provide(
        RequestChangePasswordHandler, scope=Scope.REQUEST
    )
    set_new_pwd_handler = provide(
        ResetPasswordWithTokenHandler, scope=Scope.REQUEST
    )
    delete_user_handler = provide(DeleteUserHandler, scope=Scope.REQUEST)
    add_role_to_user_handler = provide(
        AddRoleToUserHandler, scope=Scope.REQUEST
    )
    read_client_page_view_handler = provide(
        ReadClientPageViewQueryHandler, scope=Scope.REQUEST
    )
    get_all_clients_ids_handler = provide(
        GetClientsIdsHandler, scope=Scope.REQUEST
    )
    identify_by_cookies_query_handler = provide(
        IdentifyByCookiesQueryHandler, scope=Scope.REQUEST
    )
    register_resource_server_handler = provide(
        RegisterResourceServerHandler, scope=Scope.REQUEST
    )
    update_resource_server_handler = provide(
        UpdateResourceServerHandler, scope=Scope.REQUEST
    )
    get_client_resources_page_data_handler = provide(
        GetMeDataHandler, scope=Scope.REQUEST
    )
    set_user_avatar_handler = provide(
        SetUserAvatarHandler, scope=Scope.REQUEST
    )
    revoke_client_tokens_handler = provide(
        RevokeClientTokenHandler, scope=Scope.REQUEST
    )
    refresh_client_tokens_handler = provide(
        RefreshClientTokensHandler, scope=Scope.REQUEST
    )
    read_resource_server_page_view_query_handler = provide(
        ReadResourceServerPageViewQueryHandler, scope=Scope.REQUEST
    )
    delete_role_handler = provide(DeleteRoleHandler, scope=Scope.REQUEST)
    get_all_rs_ids_handler = provide(GetAllRSIdsHandler, scope=Scope.REQUEST)
    verify_reset_code_handler = provide(
        VerifyResetCodeHandler, scope=Scope.REQUEST
    )
    yandex_login_handler = provide(YandexLoginHandler, scope=Scope.REQUEST)
    yandex_register_handler = provide(
        YandexRegisterHandler, scope=Scope.REQUEST
    )
    get_user_info_query_handler = provide(
        GetUserInfoQueryHandler, scope=Scope.REQUEST
    )
    find_clients_handler = provide(FindClientsHandler, scope=Scope.REQUEST)
    find_rs_handler = provide(FindRSHandler, scope=Scope.REQUEST)
    set_client_avatar_handler = provide(
        SetClientAvatarHandler, scope=Scope.REQUEST
    )
    get_client_avatar_handler = provide(
        GetClientAvatarHandler, scope=Scope.REQUEST
    )
    get_available_accounts_handler = provide(
        GetAvailableAccountsHandler, scope=Scope.REQUEST
    )
    register_ref_handler = provide(
        RegisterRefHandler, scope=Scope.REQUEST
    )
    read_ref_page_view_query_handler = provide(
        ReadRefPageViewQueryHandler, scope=Scope.REQUEST
    )
    update_ref_command_handler = provide(
        UpdateRefCommandHandler, scope=Scope.REQUEST
    )
