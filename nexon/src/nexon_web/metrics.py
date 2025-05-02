from fastapi import APIRouter, Response
from prometheus_client import CollectorRegistry, Counter, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST 
from pathlib import Path

# Router for metrics
router = APIRouter()

# Path to audit log
AUDIT_LOG = Path.home() / ".nexon" / "audit.log"


def parse_audit_counts() -> dict[str, int]:
    """
    Parse the audit.log file and count occurrences for each action
    """
    counts: dict[str, int] = {}
    if not AUDIT_LOG.exists():
        return counts

    for line in AUDIT_LOG.read_text().splitlines():
        # Format: TIMESTAMP | user | action | target | details
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        action = parts[2]
        counts[action] = counts.get(action, 0) + 1
    return counts


@router.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics parsed from the audit log.
    """
    # Create a fresh registry
    registry = CollectorRegistry()
    # Define a counter with 'action' label
    c = Counter(
        'nexon_actions_total',
        'Total number of Nexon CLI actions recorded',
        ['action'],
        registry=registry
    )

    # Populate counts from audit log
    for action, count in parse_audit_counts().items():
        c.labels(action=action).inc(count)

    # Generate latest metrics output
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
