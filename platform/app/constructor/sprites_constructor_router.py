from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from app.dao.dao_models import SpriteDAO
from app.constructor.validation import SCharSave
from app.users.auth import decode_access_token
from app.users.router import redirect_message
from app.migration.models import Sprite


router = APIRouter(prefix='/sprites', tags=['Sprites'])


@router.post("/add_sprite/", response_model=None)
async def add_character(
    request: Request,
    sprite: SCharSave
) -> JSONResponse | RedirectResponse:
    """Сохраняет спрайт в базу данных."""
    
    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
        await SpriteDAO.add_sprite(
            email=user_id,
            sprite_name=sprite.sprite_name,
            data=sprite.data
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "Спрайт сохранён"}
        )
        
    except ExpiredSignatureError:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    except JWTError:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
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
async def get_all_sprites(
    request: Request
) -> RedirectResponse | list[Sprite] | None:
    """Возвращает все спрайты пользователя."""

    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
        sprites = await SpriteDAO.find_all_sprites(user_id=user_id)

        return sprites

    except ExpiredSignatureError:
        message = "Истек срок годности токена." 
    
    except JWTError:
        message = "Возникла ошибка при работе с токеном."

    except LookupError:
        message = "Пользователь не авторизован."

    return redirect_message(
        url='/auth/login/',
        message=message,
        error=True
    )

@router.delete("/delete_sprite/{id}/")
async def delete_sprite(
    id: int
) -> bool:
    """Удаляет спрайт пользователя."""

    return await SpriteDAO.delete_sprite(sprite_id=id)