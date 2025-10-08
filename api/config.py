from typing import Any
from fastapi import APIRouter, HTTPException, status
from config.config_manager import config_manager

# return types for this file all generic because config returns all types of jsons
router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_config() -> dict[str, Any]:
    try:
        return config_manager.config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{section}", status_code=status.HTTP_200_OK)
async def get_config_section(section: str) -> Any:
    try:
        return config_manager.get_section(section)
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Config section '{section}' not found"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{section}", status_code=status.HTTP_200_OK)
async def replace_config_section(section: str, payload: Any) -> Any:
    try:
        updated_section = config_manager.replace_section(section, payload)
        return {"section": section, "config": updated_section}
    except KeyError:
        raise HTTPException(
            status_code=404, detail=f"Config section '{section}' not found"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
