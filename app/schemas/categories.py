from datetime import datetime
from typing import Literal
from pydantic import BaseModel


CategoryType = Literal["income", "expense", "both"]


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    color: str | None = None
    type: CategoryType


class CategoryResponse(BaseModel):
    id: str
    user_id: str | None       # None si es global
    name: str
    icon: str | None
    color: str | None
    type: CategoryType
    is_global: bool
    created_at: datetime