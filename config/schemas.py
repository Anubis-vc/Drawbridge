from pydantic import BaseModel, Field, ConfigDict


class FaceRecognitionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(..., min_length=1)
    similarity_threshold: float = Field(..., gt=0, lt=1)
    providers: list[str] = Field(
        default_factory=lambda: ["CPUExecutionProvider"],
        description="Ordered ONNX Runtime providers to initialize InsightFace with.",
    )


class OverlayConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    font_scale: float = Field(..., gt=0)
    font_thickness: int = Field(..., ge=1)
    mesh: bool = Field(default=False)


class BlinkConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ear_threshold: float = Field(..., gt=0, lt=1)
    blink_consec_frames: int = Field(..., ge=1)
    blinks_to_verify: int = Field(..., ge=1)


class NotificationsServiceConfig(BaseModel):
    owner: str = Field(..., min_length=1)
    recipients: list[str] = Field(default_factory=list)


class NotificationsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled_services: list[str] = Field(default_factory=list)
    config_objects: dict[str, NotificationsServiceConfig] = Field(default_factory=dict)


class ApplicationConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    face_recognition: FaceRecognitionConfig
    blink_config: BlinkConfig
    overlay: OverlayConfig
    notifications: NotificationsConfig | None = None
