import pytest
from app.core.token_manager import TokenManager
from app.core.rbac import requires_permission
from fastapi import HTTPException


def test_token_crud(monkeypatch):
    tm = TokenManager()
    # create
    rec = tm.create_token("alice", ["env:create"], description="test", expires_in=60)
    assert rec.user == "alice" and "env:create" in rec.scopes
    # list
    tokens = tm.list_tokens()
    assert any(t.token == rec.token for t in tokens)
    # validate good
    assert tm.validate_token(rec.token, "env:create")
    # invalid scope
    assert not tm.validate_token(rec.token, "pkg:install")
    # revoke
    ok = tm.revoke_token(rec.token)
    assert ok and not tm.validate_token(rec.token, "env:create")


def dummy_func():
    return "ok"


def test_requires_permission_decorator():
    # simulate a user lacking permission
    @requires_permission("pkg:install")
    def protected():
        return "secret"
    # monkeypatch get_current_user to return guest
    import app.routers.auth as auth_mod
    auth_mod.get_current_user = lambda: {"username": "bob", "role": "guest"}

    with pytest.raises(HTTPException):
        protected()
