from pydantic import BaseModel
from typing import List, Optional


class EnvironmentModel(BaseModel):
    name: str
    created_at: str
    description: Optional[str] = ""
    role: Optional[str] = "custom"
    packages: List[str] = []
