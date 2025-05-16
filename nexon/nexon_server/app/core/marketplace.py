from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.marketplace_item import MarketplaceItem


class MarketplaceManager:
    """
    CRUD + search of marketplace items.
    """
    def __init__(self):
        self.db: Session = SessionLocal()

    def list_items(self, public_only: bool = True):
        q = self.db.query(MarketplaceItem)
        if public_only:
            q = q.filter_by(public=True)
        return q.all()

    def get_item(self, name: str, version: str):
        return self.db.query(MarketplaceItem).get((name, version))
