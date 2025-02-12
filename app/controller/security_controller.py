from fastapi import APIRouter, HTTPException, status, Depends
from app.core.security import authentication, authorization, user_context, payload_context
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


# @router.post("/change-password", status_code=status.HTTP_200_OK)
# async def change_password(request: ChangePasswordRequest, user=Depends(authentication.get_current_user)):
#     if not user:
#         raise HTTPException(status_code=401, detail="User not authenticated")

#     if not request.currentPassword or not request.newPassword:
#         raise HTTPException(status_code=400, detail="Both current and new password are required")

#     try:
#         await user_service.change_user_password(user, request.currentPassword, request.newPassword)
#         return {"message": "Password changed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/verify-password", status_code=status.HTTP_200_OK)
# async def verify_password(request: VerifyPasswordRequest, user=Depends(authentication.get_current_user)):
#     if not user:
#         raise HTTPException(status_code=401, detail="User not authenticated")

#     if not request.password:
#         raise HTTPException(status_code=400, detail="Password is required")

#     try:
#         is_valid = await user_service.verify_password(user, request.password)
#         if is_valid:
#             return {"message": "Password is correct"}
#         else:
#             raise HTTPException(status_code=400, detail="Incorrect password")
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/refresh-refresh-token", response_model=RefreshTokenResponse)
# async def refresh_refresh_token(request: RefreshTokenRequest):
#     if not request.refreshToken:
#         raise HTTPException(status_code=400, detail="Refresh token is required")

#     try:
#         new_refresh_token = authentication.refresh_refresh_token(request.refreshToken)
#         return {"refreshToken": new_refresh_token}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
