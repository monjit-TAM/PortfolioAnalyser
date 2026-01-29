"""Authentication router"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from api.models.schemas import (
    UserCreate, UserLogin, Token, APIKeyCreate, APIKeyResponse, ErrorResponse
)
from api.services.auth_service import (
    authenticate_user, create_user, create_access_token, 
    create_api_key, get_user_api_keys, revoke_api_key,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, responses={400: {"model": ErrorResponse}})
async def signup(user_data: UserCreate):
    """Register a new user account"""
    user = create_user(user_data.email, user_data.password, user_data.full_name)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=Token, responses={401: {"model": ErrorResponse}})
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password to get access token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/token", response_model=Token, responses={401: {"model": ErrorResponse}})
async def login_json(user_data: UserLogin):
    """Login with JSON body (alternative to form-based login)"""
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "full_name": current_user.get("full_name"),
        "auth_type": current_user.get("auth_type")
    }


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_new_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new API key for programmatic access"""
    api_key = create_api_key(
        user_id=current_user["id"],
        name=key_data.name,
        permissions=key_data.permissions
    )
    
    from datetime import datetime
    return APIKeyResponse(
        api_key=api_key,
        name=key_data.name,
        created_at=datetime.utcnow(),
        permissions=key_data.permissions
    )


@router.get("/api-keys")
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """List all API keys for current user"""
    keys = get_user_api_keys(current_user["id"])
    return {"api_keys": keys}


@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: int, current_user: dict = Depends(get_current_user)):
    """Revoke an API key"""
    success = revoke_api_key(current_user["id"], key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key revoked successfully"}
