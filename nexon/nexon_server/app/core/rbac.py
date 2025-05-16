from fastapi import HTTPException, status, Depends
from app.routers.auth import get_current_user


# Map roles -> allowed permission strings (support wildcard "*")
PERMISSIONS = {
    "admin": ["*"],
    "dev":   ["env:*", "pkg:*", "render:*", "ci:*", "metrics:read"],
    "qa":    ["env:read", "pkg:install", "metrics:read"],
    "guest": ["env:read", "metrics:read"]
}


def requires_permission(perm: str):
    """
    Decorator to enforce that current_user has 'perm'. Supports env:create, pkg:build, etc.
    """
    def decorator(func):
        def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            role = current_user.get("role", "")
            allowed = PERMISSIONS.get(role, [])
            if "*" not in allowed and perm not in allowed:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role}' lacks permission '{perm}'"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
