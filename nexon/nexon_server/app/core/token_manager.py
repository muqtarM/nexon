from typing import List, Type
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.api_token import APIToken
from app.db import SessionLocal


class TokenManager:
    """
    Create, list, revoke, and validate API tokens.
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def create_token(self, user: str, scopes: list[str],
                     description: str = None,
                     expires_in: int | None = None) -> APIToken:
        tok = str(uuid4())
        expires_at = (
            datetime.utcnow() + timedelta(seconds=expires_in)
            if expires_in else None
        )
        record = APIToken(
            token=tok,
            user=user,
            scopes=scopes,
            description=description,
            expires_at=expires_at
        )
        self.db.add(record)
        self.db.commit()
        return record

    def list_tokens(self) -> list[Type[APIToken]]:
        return self.db.query(APIToken).all()

    def revoke_token(self, token: str) -> bool:
        rec = self.db.query(APIToken).get(token)
        if not rec:
            return False
        self.db.delete(rec)
        self.db.commit()
        return True

    def validate_token(self, token: str, required_scope: str) -> bool:
        rec: APIToken = self.db.query(APIToken).get(token)
        if not rec:
            return False
        if rec.expires_at and rec.expires_at < datetime.utcnow():
            return False
        # scope check: wildcard or exact match
        return "*" in rec.scopes or required_scope in rec.scopes
