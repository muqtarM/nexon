import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.plugin_submission import PluginSubmission


class DeveloperPortalError(Exception):
    pass


class PortalManager:
    def __init__(self):
        self.db: Session = SessionLocal()

    def submit_plugin(self, name, repo_url, author, description):
        pid = str(uuid.uuid4())
        rec = PluginSubmission(
            id=pid, name=name, repo_url=repo_url,
            author=author, description=description
        )
        self.db.add(rec)
        self.db.commit()
        return rec

    def list_submissions(self, status="pending"):
        return self.db.query(PluginSubmission).filter_by(status=status).all()

    def review(self, pid, approve: bool, reviewer: str):
        rec = self.db.query(PluginSubmission).get(pid)
        if not rec:
            raise DeveloperPortalError("Submission not found")
        rec.status = "approved" if approve else "rejected"
        rec.reviewer = reviewer
        rec.reviewed_at = datetime.utcnow()
        self.db.commit()
        return rec
