import os
from typing import List

from app import db
from app import settings as config
from app import utils
from app.auth.jwt import get_current_user
from app.model.schema import PredictRequest, PredictResponse
from app.model.services import model_predict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Model"], prefix="/model")


@router.post("/predict")
async def predict(file: UploadFile, current_user=Depends(get_current_user)):
    rpse = {
        "success": False,
        "prediction": None,
        "score": None,
        "image_file_name": None,
    }

    if not utils.allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="File type is not supported."
        )

    file_hash = await utils.get_file_hash(file)
    file_path = os.path.join(config.UPLOAD_FOLDER, file_hash)

    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(await file.read())
        await file.seek(0)


    prediction, score = await model_predict(file_hash)


    rpse.update({
        "success": True,
        "prediction": prediction,
        "score": score,
        "image_file_name": file_hash,
    })

    return PredictResponse(**rpse)