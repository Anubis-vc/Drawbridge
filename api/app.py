from fastapi import FastAPI

from api.config import router as config_router
from api.users import router as users_router


app = FastAPI(title="Face Recognition API")

app.include_router(users_router, prefix="/users")
app.include_router(config_router, prefix="/config")


@app.get("/")
async def root():
    return {"message": "Welcome to the Face Recognition API"}
