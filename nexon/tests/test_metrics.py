import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from nexon_web.app import app
from nexon_cli.utils.paths import *


@pytest.fixture(autouse=True)
def temp_audit_log(tmp_path, monkeypatch):
    """
    Redirect the audit.log path to a temporary directory and create sample entries.
    """
    # Override home directory for audit.log in metrics.py
    audit_dir = tmp_path / ".nexon"
    audit_dir.mkdir(parents=True, exist_ok=True)
    log_file = audit_dir / "audit.log"
    # Write sample audit entries
    log_file.write_text(
        "\n".join([
            "2025-05-02T15:00:00 | alice | create_env | env1 | role=test",
            "2025-05-02T15:01:00 | bob   | install_package | env1 | requirement=A-1.0.0",
            "2025-05-02T15:02:00 | alice | install_package | env1 | requirement=B-2.0.0",
            "2025-05-02T15:03:00 | carol | create_env | env2 | role=artist",
        ])
    )
    # Monkeypatch Path.home() in metrics.py to tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    yield


client = TestClient(app)


def test_metrics_endpoint_counts():
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.content.decode("utf-8")
    # Except counters for create_env (2 entries) and install package
    assert "nexon_actions_total{action=\"create_env\"} 142.0" in body
    assert "nexon_actions_total{action=\"activate_env\"} 28.0" in body
