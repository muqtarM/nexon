from fastapi import APIRouter, HTTPException
from typing import List
from nexon_cli.core.env_manager import EnvironmentManager
from nexon_web.models.env_model import EnvSummary, EnvDetail

router = APIRouter()


@router.get("/", response_model=List[EnvSummary])
def list_envs():
    mgr = EnvironmentManager()
    files = mgr.list_environments(return_data=True)
    return files


@router.get("/{env_name}", response_model=EnvDetail)
def get_env(env_name: str):
    mgr = EnvironmentManager()
    try:
        return mgr.get_environment(env_name)    # stub for loading full YAML
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Environment not found")
