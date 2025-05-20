import contextvars
import os

# CLI-level tenant context
_cli_tenant: contextvars.ContextVar[str] = contextvars.ContextVar("cli_tenant")


class CLITenantManager:
    """
    Manages tenant context for the CLI.
    """

    @staticmethod
    def set_tenant(tenant_id: str):
        if not tenant_id or not tenant_id.strip():
            raise ValueError("Tenant ID must be provided")
        _cli_tenant.set(tenant_id)

    @staticmethod
    def get_tenant() -> str:
        try:
            return _cli_tenant.get()
        except LookupError:
            # fallback to env var NEXON_TENANT
            tenant = os.getenv("NEXON_TENANT")
            if not tenant:
                raise RuntimeError("No tenant specified. Use --tenant or set NEXON_TENANT.")
            _cli_tenant.set(tenant)
            return tenant
