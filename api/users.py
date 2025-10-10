from api.data_validation import UserCreate, UserResponse, ImageResponse
from database.data_operations import db

from fastapi import APIRouter, HTTPException, UploadFile, File
import cv2
from insightface.app import FaceAnalysis
import numpy as np


router = APIRouter()


model = "buffalo_s"
embedding_service = FaceAnalysis(
    name=model, providers=["CPUExecutionProvider"]
)  # change to gpu later
embedding_service.prepare(ctx_id=0, det_size=(640, 640))


@router.post("/", status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    try:
        user_id = db.add_user(user.name, user.access_level.value)
        return UserResponse(
            id=user_id, name=user.name, access_level=user.access_level, num_embeddings=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", status_code=200)
async def get_all_users() -> list[UserResponse]:
    try:
        users = db.get_all_users()
        return [
            UserResponse(
                id=user["id"],
                name=user["name"],
                access_level=user["access_level"],
                num_embeddings=user["num_embeddings"],
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", status_code=200)
async def get_user(user_id: int) -> UserResponse:
    try:
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(
            id=user["id"],
            name=user["name"],
            access_level=user["access_level"],
            num_embeddings=user["num_embeddings"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    try:
        db.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/images", status_code=201)
async def add_image(
    user_id: int, img_name: str, image: UploadFile = File(...)
) -> ImageResponse:
    """
    Generate and store the face embedding for a user
    Accepts any valid image format that cv2 can decode
    Max size 10MB
    """
    try:
        # make sure that the user exists
        user = db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # read in the image file
        image_bytes = await image.read()

        # find the face embedding
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        faces = embedding_service.get(img)
        if not faces:
            raise HTTPException(status_code=400, detail="No face found in image")
        # take largest face if multiple
        face = max(
            faces,
            key=lambda f: ((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])),
        )
        normed_embedding = face.normed_embedding

        # add the embedding to the table
        db.add_image(img_name, user_id, normed_embedding)

        return ImageResponse(
            img_name=img_name,
            user_id=user_id,
            message="Successfully added image and embedding to user",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/images/{img_name}", status_code=200)
async def delete_image(user_id: int, img_name: str):
    try:
        db.delete_image(img_name, user_id)
        return {"message": "Image successfully deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
