from pydantic import BaseModel
from datetime import datetime


class AuditEntryOut(BaseModel):
    id: int
    timestamp: datetime
    user: str
    action: str
    target: str
    details: str | None

    class Config:
        orm_mode = True
