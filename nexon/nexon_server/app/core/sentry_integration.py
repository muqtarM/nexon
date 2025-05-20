import logging
import os
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI


def wrap_app_with_sentry(app: FastAPI) -> FastAPI | SentryAsgiMiddleware:
    dsn = os.getenv("SENTRY_DSN_SERVER")
    if not dsn:
        return app

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.2,
        environment=os.getenv("NEXON_ENV", "development"),
        integrations=[
            LoggingIntegration(
                level=None,
                event_level=logging.ERROR
            )
        ]
    )
    return SentryAsgiMiddleware(app)
