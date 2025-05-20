from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway, CONTENT_TYPE_LATEST
import os

# Use a separate registry to avoid conflicts with server
registry = CollectorRegistry()
CLI_COMMANDS = Counter(
    "nexon_cli_commands_total",
    "Total Nexon CLI commands invoked",
    ["command"], registry=registry
)
COMMAND_DURATION = Histogram(
    "nexon_cli_command_duration_seconds",
    "Duration of Nexon CLI commands",
    ["command"], registry=registry
)


def record_cli_metrics(command_name: str, duration: float):
    CLI_COMMANDS.labels(command=command_name).inc()
    COMMAND_DURATION.labels(command=command_name).observe(duration)


def push_metrics():
    gateway = os.getenv("PROMETHEUS_PUSHGATEWAY")
    if gateway:
        push_to_gateway(gateway, job="nexon_cli", registry=registry)
