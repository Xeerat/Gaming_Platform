from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError
from app.database import async_session_maker
from sqlalchemy import select

from app.dao.dao_models import MapDAO
from app.constructor.validation import SMapSave
from app.users.auth import decode_access_token
from app.users.router import redirect_message
from app.migration.models import Map


router = APIRouter(prefix='/maps', tags=['Maps'])


@router.post("/add_map/", response_model=None)
async def add_map(
    request: Request,
    map_data: SMapSave
) -> JSONResponse | RedirectResponse:
    """Сохраняет карту в базу данных."""
    
    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
        await MapDAO.add_map(
            user_id=user_id,
            mapname=map_data.map_name,
            data=map_data.data
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "message": "Карта сохранёна"}
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
            content={"detail": "Карта с таким именем уже существует"}
        )
    
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка базы данных"}
        )
    

@router.get("/get_all_maps/", response_model=None)
async def get_all_maps(
    request: Request
) -> RedirectResponse | list[Map] | None:
    """Возвращает все карты пользователя."""

    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )

    try:
        user_id = decode_access_token(token)
        maps = await MapDAO.find_all_maps(user_id=user_id)

        return maps
        
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


@router.delete("/delete_map/{id}/")
async def delete_map(
    id: int
) -> bool:
    """Удаляет карту пользователя."""

    return await MapDAO.delete_map(map_id=id)


@router.get("/get_map/{map_id}/")
async def get_map_by_id(map_id: int):
    """Возвращает карту по ID."""
    async with async_session_maker() as session:
        query = select(Map).where(Map.id == map_id)
        result = await session.execute(query)
        map_data = result.scalar_one_or_none()
        
        if not map_data:
            return JSONResponse(status_code=404, content={"detail": "Карта не найдена"})
        
        return {
            "id": map_data.id,
            "data": map_data.data,
            "mapname": map_data.mapname
        }