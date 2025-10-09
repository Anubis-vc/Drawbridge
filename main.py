from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status

from api.config import router as config_router
from api.users import router as users_router
from api.state import State


@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = State()
    app.state.runtime = runtime
    try:
        yield
    finally:
        video_task = runtime._video_task
        if video_task and not video_task.done():
            runtime._stop_signal.set()
            await video_task


app = FastAPI(title="Face Recognition Service", lifespan=lifespan)
app.include_router(users_router, prefix="/users")
app.include_router(config_router, prefix="/config")


def get_runtime() -> State:
    runtime = getattr(app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Runtime state not initialised",
        )
    return runtime


@app.post("/video/toggle")
async def toggle_video(runtime: State = Depends(get_runtime)) -> dict[str, str]:
    status = await runtime.toggle_video()
    return {"status": status}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Face Recognition service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)
