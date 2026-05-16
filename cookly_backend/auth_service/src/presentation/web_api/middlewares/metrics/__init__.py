import os

from fastapi import FastAPI

from .middleware import PrometheusMiddleware
from .utils import metrics, setting_telemetry

APP_NAME = "api"
GRPC_ENDPOINT = os.getenv("GRPC_ENDPOINT", "http://backend_service.tempo:4317")


def add_metrics_middleware(app: FastAPI):
    app.add_middleware(PrometheusMiddleware, app_name=APP_NAME)
    app.add_route("/metrics", metrics)
    setting_telemetry(app, APP_NAME, GRPC_ENDPOINT)
