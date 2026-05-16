from dishka import Provider, Scope, provide

from application.client.client_ref.common.reader import RefReader
from application.client.common.client_reader import ClientReader
from application.common.interfaces.user_reader import UserReader
from application.resource_server.common.rs_reader import ResourceServerReader
from infrastructure.db.readers.client_reader import ClientReaderImpl
from infrastructure.db.readers.ref_reader import RefReaderImpl
from infrastructure.db.readers.rs_reader import ResourceServerReaderImpl
from infrastructure.db.readers.user_reader import UserReaderImpl


class ReaderProvider(Provider):
    user_reader = provide(
        UserReaderImpl, scope=Scope.REQUEST, provides=UserReader
    )
    client_reader = provide(
        ClientReaderImpl, scope=Scope.REQUEST, provides=ClientReader
    )
    resource_server_reader = provide(
        ResourceServerReaderImpl,
        scope=Scope.REQUEST,
        provides=ResourceServerReader,
    )
    ref_reader = provide(RefReaderImpl, scope=Scope.REQUEST, provides=RefReader)
    # strategy_reader = provide(StrategyReader, scope=Scope.REQUEST)
