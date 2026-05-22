from fastapi import APIRouter, Depends, UploadFile, File
from app.dependencies import get_current_user
from app.schemas.users import ProfileResponse, UpdateProfileRequest
from app.services import users as users_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ProfileResponse)
def get_me(user: dict = Depends(get_current_user)):
    return users_service.get_profile(user["sub"])


@router.patch("/me", response_model=ProfileResponse)
def update_me(data: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    return users_service.update_profile(user["sub"], data)


@router.post("/me/avatar", response_model=ProfileResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    content_type = file.content_type or "image/jpeg"
    file_bytes = await file.read()
    avatar_url = users_service.upload_avatar_to_storage(user["sub"], file_bytes, content_type)
    return users_service.update_avatar(user["sub"], avatar_url)