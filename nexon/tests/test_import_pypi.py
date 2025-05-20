from typer.testing import CliRunner
import pytest
from nexon_cli.cli import cli

runner = CliRunner()


def test_import_pypi_dry(tmp_path, monkeypatch):
    # Override packages dir
    monkeypatch.setenv("NEXON_BASE_DIR", str(tmp_path))
    # run with a simple local wheel instead of PyPI
    wheel = tmp_path / "pkg-1.0.0.whl"
    wheel.write_text("")    # placeholder
    result = runner.invoke(cli, ["import-wheel", str(wheel)])
    assert result.exit_code == 0
    assert "Imported pkg-1.0.0" in result.stdout 
