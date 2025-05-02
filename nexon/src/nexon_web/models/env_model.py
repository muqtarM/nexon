from pydantic import BaseModel
from typing import List


class EnvSummary(BaseModel):
    name: str
    role: str


class EnvDetail(EnvSummary):
    packages: List[str]
    created_at: str
