from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List
from app.core.rbac import requires_permission
from app.routers.auth import get_current_user
from nexon_cli.core.env_manager import EnvironmentManager
from nexon_cli.core.package_manager import PackageManager
from nexon_cli.core.dependency_solver import DependencySolver

router = APIRouter(prefix="/preview", tags=["preview"])


@router.get("/envs", response_model=List[Dict[str, Any]])
@requires_permission("env:read")
def list_envs(current_user=Depends(get_current_user)):
    em = EnvironmentManager()
    return em.list_environments()


@router.get("/packages", response_model=List[Dict[str, Any]])
@requires_permission("pkg:read")
def list_packages(current_user=Depends(get_current_user)):
    pm = PackageManager()
    return pm.list_packages()


@router.get("/graph", response_model=Dict[str, Any])
@requires_permission("graph:read")
def dependency_graph(env: str, current_user=Depends(get_current_user())):
    solver = DependencySolver()
    try:
        # reuse graph endpoint logic
        return solver.graph(env)
    except Exception as e:
        raise HTTPException(404, str(e))
