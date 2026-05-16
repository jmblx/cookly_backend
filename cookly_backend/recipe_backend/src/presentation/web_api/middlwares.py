from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from presentation.web_api.tz_context import TimezoneMiddleware


def setup_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimezoneMiddleware)
