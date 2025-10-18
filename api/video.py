from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
import asyncio

from runtime_services.state import State


router = APIRouter()


# gets the universal runtime state object
def get_runtime(request: Request) -> State:
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Runtime state not available")
    return runtime


@router.get("/start")
async def video_start(runtime: State = Depends(get_runtime)):
    return {"video_status": await runtime.start_video()}


@router.get("/stop")
async def video_stop(runtime: State = Depends(get_runtime)):
    return {"video_status": await runtime.stop_video()}


@router.get("/status")
async def video_status(runtime: State = Depends(get_runtime)):
    return {"video_status": "Running" if runtime.is_video_running() else "Stopped"}


@router.get("/stream")
async def stream_video(runtime: State = Depends(get_runtime)):
    async def frame_generator():
        while runtime.is_video_running():
            if runtime.latest_frame_buffer:
                # Yield as multipart data
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + runtime.latest_frame_buffer.tobytes()
                    + b"\r\n"
                )
            await asyncio.sleep(0.03)  # about 30 fps

    # https://stackoverflow.com/questions/21197638/create-a-mjpeg-stream-from-jpeg-images-in-python
    return StreamingResponse(
        frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )
