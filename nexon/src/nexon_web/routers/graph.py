from fastapi import APIRouter, HTTPException
from typing import Dict, List
from pydantic import BaseModel
from nexon_cli.core.dependency_solver import DependencySolver, DependencyError

router = APIRouter()


class GraphRequest(BaseModel):
    requirements: List[str]


@router.post("", response_model=Dict[str, List[str]])
@router.post("/", response_model=Dict[str, List[str]])
def build_graph(request: GraphRequest):
    solver = DependencySolver()
    try:
        return solver.build_graph(request.requirements)
    except DependencyError as e:
        raise HTTPException(status_code=400, detail=str(e))
