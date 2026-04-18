from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from app.dao.dao_models import SpriteDAO, SpriteLogicDAO
from app.constructor.validation import SCharSave, SLogic
from app.users.auth import decode_access_token
from app.users.router import redirect_message
from app.migration.models import Sprite, SpriteLogic


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
            user_id=user_id,
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


@router.get("/get_sprite_logic/{sprite_name}/", response_model=None)
async def get_sprite_logic(
    request: Request,
    sprite_name: str
) -> RedirectResponse | list[SpriteLogic] | None:
    """Возвращает все блоки логики для указанного спрайта."""

    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
        sprite = await SpriteDAO.find_sprite(
            user_id=user_id,
            sprite_name=sprite_name
        )
        if not sprite:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Спрайт не найден"}
            )
        logics = await SpriteLogicDAO.find_all_sprite_logic_by_sprite(
            sprite_id=sprite.id
        )

        return logics if logics else []

    except ExpiredSignatureError:
        message = "Истек срок годности токена." 
    
    except JWTError:
        message = "Возникла ошибка при работе с токеном."

    except SQLAlchemyError:
        message = "Ошибка базы данных при получении логики."

    return redirect_message(
        url='/auth/login/',
        message=message,
        error=True
    )


@router.post("/update_sprite_logic/", response_model=None)
async def update_sprite_logic(
    request: Request,
    logic: SLogic
) -> JSONResponse:
    """
    Добавляет блок логики, если не было блока с таким именем
    у выбранного спрайта. Обновляет информацию о блоке в ином случае
    
    """

    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id =  decode_access_token(token)
        sprite = await SpriteDAO.find_sprite(
            user_id=user_id,
            sprite_name=logic.sprite_name
        )
        logic_block = await SpriteLogicDAO.find_sprite_logic_block(
            sprite_id=sprite.id,
            logic_block_name=logic.name
        )
        if logic_block:
            await SpriteLogicDAO.update_sprite_logic(
                logic_id=logic_block.id,
                trigger_config=logic.trigger_config,
                dialog_config=logic.dialog_config,
                dialog_role=logic.dialog_role
            )

        else :
            await SpriteLogicDAO.add_sprite_logic(
                sprite_id=sprite.id,
                name=logic.name,
                trigger_config=logic.trigger_config,
                dialog_config=logic.dialog_config,
                dialog_role=logic.dialog_role
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "Блок логики обновлён"}
        )
        
    except ExpiredSignatureError:
        return redirect_message(
            url='/auth/login/',
            message="Истек срок годности токена.",
            error=True
        )    
    
    except JWTError:
        return redirect_message(
            url='/auth/login/',
            message="Возникла ошибка при работе с токеном.",
            error=True
        )
    
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка базы данных при обновлении"}
        )