import aiohttp
from dishka import Provider, Scope, provide

from core.config import AuthCoreConfig


class HttpSessionProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=aiohttp.ClientSession)
    async def provide_http_session(self, config: AuthCoreConfig) -> aiohttp.ClientSession:
        connector = aiohttp.TCPConnector(ssl=config.api_url.startswith("http://"))
        async with aiohttp.ClientSession(connector=connector) as session:
            yield session
