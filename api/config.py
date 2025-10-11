from typing import Any
from fastapi import APIRouter, HTTPException, status
from config.config_manager import config_manager
from utils.schemas import (
    FaceRecognitionConfig,
    NotificationsConfig,
    BlinkConfig,
    OverlayConfig,
)
from utils.enums import ConfigSections

# return types for this file all generic because config returns all types of jsons
router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_config() -> dict[str, Any]:
    try:
        return config_manager.config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{section}", status_code=status.HTTP_200_OK)
async def get_config_section(section: ConfigSections) -> dict:
    try:
        return config_manager.get_section(section.value)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Config section '{section.value}' not found"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{section}", status_code=status.HTTP_200_OK)
async def replace_config_section(
    section: ConfigSections,
    payload: FaceRecognitionConfig | NotificationsConfig | BlinkConfig | OverlayConfig,
) -> dict:
    try:
        updated_section = config_manager.replace_section(
            section.value, payload.model_dump()
        )
        return {"section": section.value, "config": updated_section}
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Config section '{section.value}' not found"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
