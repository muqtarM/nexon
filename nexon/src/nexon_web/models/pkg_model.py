from pydantic import BaseModel
from typing import List


class PackageSummary(BaseModel):
    name: str
    versions: List[str]
