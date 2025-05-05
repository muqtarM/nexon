from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class EnvironmentBase(BaseModel):
    role: str
    packages: List[str]


class EnvironmentCreate(EnvironmentBase):
    name: str


class EnvironmentUpdate(BaseModel):
    role: Optional[str] = None
    packages: Optional[List[str]] = None


class EnvironmentOut(EnvironmentBase):
    name: str
    created_at: datetime

    class Config:
        orm_mode = True
