from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request

from ..config import TRACING
from .metrics import add_metrics_middleware


import json
from starlette.types import ASGIApp, Scope, Receive, Send

class ExtractRefreshTokenMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = b""
        more_body = True

        async def receive_wrapper():
            nonlocal body, more_body

            message = await receive()

            if message["type"] == "http.request":
                body += message.get("body", b"")
                more_body = message.get("more_body", False)

                if not more_body and "refresh_token" not in scope:
                    try:
                        data = json.loads(body)
                        scope["refresh_token"] = data.get("refresh_token")
                    except Exception:
                        scope["refresh_token"] = None

            return message

        await self.app(scope, receive_wrapper, send)


def setup_middlewares(app: FastAPI):
    if TRACING:
        add_metrics_middleware(app)
    app.add_middleware(ExtractRefreshTokenMiddleware)

    # app.add_middleware(
    #     CORSMiddleware,
    #     # allow_origins=["https://menoitami.ru"],  # или "*" для разработки
    #     allow_origins=["*"],
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )
    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["menoitami.ru"]
    # )
