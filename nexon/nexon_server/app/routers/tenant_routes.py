from fastapi import APIRouter, Depends
from app.core.tenant_manager import TenantManager
from app.core.env_manager import EnvironmentManager

router = APIRouter(prefix="/t/{tenant}/envs", tags=["tenant-envs"])


@router.get("/", response_model=list)
def list_envs(tenant: str = Depends(TenantManager.get_tenant)):
    em = EnvironmentManager(tenant_id=tenant)
    return em.list_environments()
