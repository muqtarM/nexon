import os
from pathlib import Path
import tempfile
import pytest

from nexon_cli.core.snapshot_manager import SnapshotManager
from nexon_cli.core.configs import config


@pytest.fixture(autouse=True)
def isolate_base_dir(tmp_path, monkeypatch):
    # override base dir
    base = tmp_path / "nexon_home"
    monkeypatch.setenv("NEXON_BASE_DIR", str(base))
    yield


def test_create_and_restore(tmp_path):
    sm = SnapshotManager()
    # create some file
    f = Path(config.base_dir) / "foo.txt"
    f.write_text("hello")
    name = sm.create("snap1")
    assert name == "snap1"
    # modify
    f.write_text("changed")
    # restore
    sm.restore("snap1")
    assert f.read_text() == "hello"
