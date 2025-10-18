from __future__ import annotations
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import router as config_router
from api.users import router as users_router
from api.video import router as video_router
from runtime_services.state import State

# have fastapi manage the runtime state class and automatically clean up after use
@asynccontextmanager
async def lifespan(app: FastAPI):
    runtime = State()
    app.state.runtime = runtime
    try:
        yield
    finally:  # make sure video released properly when app is shut down
        video_task = runtime._video_task
        if video_task and not video_task.done():
            runtime._stop_signal.set()
            await video_task


app = FastAPI(title="Face Recognition Service", lifespan=lifespan)

allowed_origins = {
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users_router, prefix="/users")
app.include_router(config_router, prefix="/config")
app.include_router(video_router, prefix="/video")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Face Recognition service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)
