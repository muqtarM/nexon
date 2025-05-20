from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request
from starlette.responses import Response

from app.core.tenant_manager import TenantManager


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Option A: Path-prefix routing: /t/{tenant}/...
        path_parts = request.url.path.split("/")
        if len(path_parts) > 2 and path_parts[1] == "t":
            tenant_id = path_parts[2]
        else:
            # Option B: Subdomain routing, e.g. tenant.api.yourdomain.com
            host = request.headers.get("host", "")
            tenant_id = host.split(".")[0]
        TenantManager.set_tenant(tenant_id)
        # Strip prefix if using path-prefix
        # request.scope["path"] = "/" + "/".join(path_parts[3:]
        response = await call_next(request)
        return response
