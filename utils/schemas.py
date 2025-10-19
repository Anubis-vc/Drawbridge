from pydantic import BaseModel, EmailStr, ConfigDict
from utils.enums import AccessLevel


# USERS API SCHEMAS
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


# CONFIG API SCHEMAS
class FaceRecognitionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    similarity_threshold: float


class EmailConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: EmailStr
    recipients: list[EmailStr]


class SmsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipients: list[str]


class NotificationConfigObjects(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailConfig | None = None
    sms: SmsConfig | None = None


class NotificationsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled_services: list[str]
    config_objects: NotificationConfigObjects


class BlinkConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ear_threshold: float
    blink_consec_frames: int
    blinks_to_verify: int


class OverlayConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    font_scale: float
    font_thickness: int
    mesh: bool = False


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    face_recognition: FaceRecognitionConfig
    notifications: NotificationsConfig
    blink_config: BlinkConfig
    overlay: OverlayConfig
