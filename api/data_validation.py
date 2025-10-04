from pydantic import BaseModel
from utils.enums import AccessLevel


class UserCreate(BaseModel):
    name: str
    access_level: AccessLevel


class UserResponse(BaseModel):
    id: int
    name: str
    access_level: AccessLevel
    num_embeddings: int | None


class ImageResponse(BaseModel):
    img_name: str
    user_id: int
    message: str
