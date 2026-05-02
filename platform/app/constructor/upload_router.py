import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pathlib import Path

from app.users.auth import decode_access_token
from jose.exceptions import ExpiredSignatureError, JWTError

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path("uploads/novels")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/file/")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
):
    token = request.cookies.get("users_access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_id = decode_access_token(token)
    except (ExpiredSignatureError, JWTError):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Генерируем уникальное имя
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / unique_name

    # Сохраняем файл
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Возвращаем URL для доступа к файлу
    file_url = f"/uploads/novels/{user_id}/{unique_name}"
    return JSONResponse(content={"url": file_url})