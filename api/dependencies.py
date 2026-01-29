"""FastAPI dependencies for authentication and authorization"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from typing import Optional

from api.services.auth_service import decode_token, validate_api_key, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> dict:
    """Authenticate user via JWT token or API key"""
    
    if api_key:
        api_key_data = validate_api_key(api_key)
        if api_key_data:
            return {
                "id": api_key_data["user_id"],
                "email": api_key_data["email"],
                "full_name": api_key_data.get("full_name"),
                "permissions": api_key_data.get("permissions", []),
                "auth_type": "api_key"
            }
    
    if token:
        payload = decode_token(token)
        if payload:
            email = payload.get("sub")
            if email:
                user = get_user_by_email(email)
                if user:
                    user["auth_type"] = "jwt"
                    user["permissions"] = ["read", "write"]
                    return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[dict]:
    """Optionally authenticate user (for public endpoints with optional auth)"""
    try:
        return await get_current_user(token, api_key)
    except HTTPException:
        return None


def require_permission(permission: str):
    """Dependency factory to require specific permission"""
    async def permission_checker(user: dict = Depends(get_current_user)):
        if permission not in user.get("permissions", []) and "admin" not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user
    return permission_checker
