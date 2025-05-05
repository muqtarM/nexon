from pydantic import BaseModel
from typing import Dict, Any


class PackageBase(BaseModel):
    description: str
    spec: Dict[str, Any]


class PackageCreate(PackageBase):
    name: str
    version: str


class PackageOut(PackageBase):
    name: str
    version: str

    class Config:
        orm_mode = True
