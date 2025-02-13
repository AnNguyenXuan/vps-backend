from fastapi import APIRouter, HTTPException, status
from app.core.security import authentication, user_context, payload_context
from app.service.user_service import UserService
from app.schema.auth_schema import (
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    RefreshTokenResponse,
    ChangePasswordRequest,
    VerifyPasswordRequest,
    RefreshTokenRequest
)



user_service = UserService()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    access_token, refresh_token = await authentication.login(request)
    return {"accessToken": access_token, "refreshToken": refresh_token}


@router.post("/refresh-token", response_model=AccessTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    try:
        access_token = await authentication.refresh_access_token(request.refreshToken)
        return {"accessToken": access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout():
    try:
        await authentication.logout(payload_context.get())
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(request: ChangePasswordRequest):
    current_user = user_context.get()
    if current_user is None:
        raise HTTPException(status_code=401, detail="You have not logged in")
    try:
        await user_service.change_user_password(current_user, request.currentPassword, request.newPassword)
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-password", status_code=status.HTTP_200_OK)
async def verify_password(request: VerifyPasswordRequest):
    current_user = user_context.get()
    if current_user is None:
        raise HTTPException(status_code=401, detail="You have not logged in")
    await user_service.verify_user_password(current_user.username, request.password)
    return {"message": "Password is correct"}



@router.post("/refresh-refresh-token", response_model=RefreshTokenResponse)
async def refresh_refresh_token(request: RefreshTokenRequest):
    try:
        new_refresh_token = await authentication.refresh_refresh_token(request.refreshToken)
        return {"refreshToken": new_refresh_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
