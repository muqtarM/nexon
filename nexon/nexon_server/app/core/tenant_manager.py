import contextvars
from fastapi import HTTPException


# Holds the current tenant ID for this request
_current_tenant: contextvars.ContextVar[str] = contextvars.ContextVar("tenant_id")


class TenantManager:
    @staticmethod
    def set_tenant(tenant_id: str):
        # Validate tenant existence (e.g. in DB or config)
        if not TenantManager._exists(tenant_id):
            raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")
        _current_tenant.set(tenant_id)

    @staticmethod
    def get_tenant() -> str:
        try:
            return _current_tenant.get()
        except LookupError:
            raise HTTPException(status_code=400, detail="No tenant specified")

    @staticmethod
    def _exists(tenant_id: str) -> bool:
        # TODO: implement actual lookup (e.g. query tenants table)
        return True
