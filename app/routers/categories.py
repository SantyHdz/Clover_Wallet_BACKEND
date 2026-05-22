from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.categories import CategoryCreate, CategoryResponse
from app.services import categories as categories_service

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
def get_categories(user: dict = Depends(get_current_user)):
    return categories_service.get_categories(user["sub"])


@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, user: dict = Depends(get_current_user)):
    return categories_service.create_category(user["sub"], data)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: str, user: dict = Depends(get_current_user)):
    categories_service.delete_category(user["sub"], category_id)