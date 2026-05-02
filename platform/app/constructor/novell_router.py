from fastapi import APIRouter, Request, status, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException

from app.dao.dao_models import NovelsDAO
from app.constructor.novell_validation import SNovelSave
from app.users.auth import decode_access_token
from app.users.router import redirect_message


router = APIRouter(prefix='/novels', tags=['Novels'])


@router.post("/add_novel/", response_model=None)
async def add_novel(
    request: Request,
    novel_data: SNovelSave
) -> JSONResponse | RedirectResponse:
    """Сохраняет новеллу (проект) в базу данных."""
    
    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
        novel_id = await NovelsDAO.add_novel(
            user_id=user_id,
            title=novel_data.title,
            data=novel_data.data,
            preview=novel_data.preview
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ok",
                "message": "Новелла сохранена",
                "id": novel_id
            }
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
            content={"detail": "Новелла с таким названием уже существует"}
        )
    
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Ошибка базы данных"}
        )

@router.get("/by_title/{title}/", response_model=None)
async def get_novel_by_title(
    title: str,
    request: Request
):
    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(
            url='/auth/login/',
            message="Пользователь не авторизован.",
            error=True
        )
    
    try:
        user_id = decode_access_token(token)
    except (ExpiredSignatureError, JWTError):
        return redirect_message(
            url='/auth/login/',
            message="Ошибка авторизации.",
            error=True
        )
    
    novel = await NovelsDAO.find_by_title(user_id, title)
    if not novel:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Новелла с названием '{title}' не найдена"}
        )
    
    # Возвращаем только data (или весь объект, но data — самое главное)
    return JSONResponse(content={
        "id": novel.id,
        "title": novel.title,
        "data": novel.data,
        "created_at": novel.created_at.isoformat(),
        "updated_at": novel.updated_at.isoformat()
    })

@router.get("/public/")
async def get_public_novels(skip: int = 0, limit: int = 6):
    novels, total = await NovelsDAO.find_paginated_all(skip, limit)
    return {
        "items": [
            {
                "id": n.id,
                "title": n.title,
                "preview": n.preview
            }
            for n in novels
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }



templates = Jinja2Templates(directory="app/site/templates")

@router.get("/game/{novel_id}")
async def game_page(request: Request, novel_id: int):
    return templates.TemplateResponse("game.html", {"request": request, "novel_id": novel_id})

@router.get("/game/{novel_id}/data")
async def get_novel_data(novel_id: int):
    novel = await NovelsDAO.find_by_id(novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Новелла не найдена")
    return novel.data