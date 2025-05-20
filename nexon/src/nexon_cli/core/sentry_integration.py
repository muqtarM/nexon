import logging
import os
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    dsn = os.getenv("SENTRY_DSN_CLI")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.1,
        environment=os.getenv("NEXON_ENV", "development"),
        integrations=[
            LoggingIntegration(
                level=None,     # capture all log levels
                event_level=logging.ERROR     # send errors as events
            )
        ]
    )
