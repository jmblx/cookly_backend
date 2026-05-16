from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(app, database_engine):
    # Define resource attributes
    resource = Resource(
        attributes={
            "service.name": "backend-service",
            "service.version": "1.0.0",
        }
    )

    # Set up tracer provider
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Configure exporter (OTLP -> Loki, Jaeger, etc.)
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://backend_service.loki:4317", insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Instrument libraries
    FastAPIInstrumentor.instrument_app(app)
    AsyncPGInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument(engine=database_engine)
    LoggingInstrumentor().instrument()
