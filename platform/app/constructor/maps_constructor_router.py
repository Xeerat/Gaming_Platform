from fastapi import APIRouter, Form, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from app.dao.dao_models import MapDAO
from app.constructor.validation import SMapSave
from app.users.auth import decode_access_token

from urllib.parse import quote


router = APIRouter(prefix='/maps', tags=['Maps'])

@router.post("/add_map/")
async def add_map(
    request: Request,
    map_data: SMapSave
):
    """Сохраняет карту"""
    
    token = request.cookies.get("users_access_token")
    try:
        email = decode_access_token(token)
        await MapDAO.add_map(
            email=email,
            mapname=map_data.map_name,
            data=map_data.data
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "Карта сохранёна"}
        )
        
    except ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Сессия истекла. Войдите заново."}
        )
    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Не авторизован"}
        )
    except IntegrityError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Карта с таким именем уже существует"}
        )
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка базы данных"}
        )