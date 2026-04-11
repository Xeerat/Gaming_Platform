from fastapi import APIRouter, Form, Request, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from app.dao.dao_models import SpriteDAO
from app.constructor.validation import SCharSave
from app.users.auth import decode_access_token
from app.users.router import redirect_message
from app.migration.models import Sprite


router = APIRouter(prefix='/sprites', tags=['Sprites'])

@router.post("/add_sprites/")
async def add_character(
    request: Request,
    sprite: SCharSave
):
    """Сохраняет спрайта"""
    
    token = request.cookies.get("users_access_token")
    try:
        email = decode_access_token(token)
        await SpriteDAO.add_sprite(
            email=email,
            sprite_name=sprite.sprite_name,
            data=sprite.data
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "Спрайт сохранён"}
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
            content={"detail": "Спрайт с таким именем уже существует"}
        )
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка базы данных"}
        )
    

@router.get("/get_all_sprites/", response_model=None)
async def get_all_sprites(request: Request) -> RedirectResponse | list[Sprite]:
    """Возвращает все спрайты пользователя."""

    token = request.cookies.get("users_access_token")

    if not token:
        return redirect_message(url='/auth/login/')
    
    try:
        email = decode_access_token(token)
        return await SpriteDAO.find_all_sprites(email=email)
        
    except JWTError:
        return redirect_message(url='/auth/login/')

    except LookupError:
        return redirect_message(url='/auth/login/')
    