from datetime import datetime
from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    full_name: str | None
    avatar_url: str | None
    provider: str
    currency: str
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    currency: str | None = None