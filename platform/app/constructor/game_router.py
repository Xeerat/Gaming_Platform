from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from app.dao.dao_models import SceneDAO, MapDAO
from app.constructor.validation import SSceneSave
from app.users.auth import decode_access_token
from app.users.router import redirect_message
from app.migration.models import Scene


router = APIRouter(prefix='/scenes', tags=['Scenes'])


@router.post("/save_scene/", response_model=None)
async def save_scene(
    request: Request,
    scene_data: SSceneSave
):
    """Сохраняет или обновляет сцену (при одинаковом названии - перезаписывает)."""
    
    token = request.cookies.get("users_access_token")
    if not token:
        return redirect_message(...)
    
    try:
        user_id = decode_access_token(token)
        
        # Проверяем существование карты
        map_obj = await MapDAO.find_map_by_id(scene_data.map_id, user_id)
        if not map_obj:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Карта не найдена"}
            )
        
        # Проверяем, есть ли уже сцена с таким названием
        existing_scene = await SceneDAO.find_scene_by_name(
            user_id=user_id,
            scene_name=scene_data.scene_name
        )
        
        if existing_scene:
            # Если сцена существует, проверяем есть ли preview
            if not existing_scene.preview_url and not scene_data.preview_url:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": "Для новой сцены необходимо добавить превью"
                    }
                )
            
            # Обновляем существующую сцену
            update_data = {
                "map_id": scene_data.map_id,
                "objects": scene_data.objects
            }
            if scene_data.preview_url:
                update_data["preview_url"] = scene_data.preview_url
            
            await SceneDAO.update_scene_by_name(
                user_id=user_id,
                scene_name=scene_data.scene_name,
                **update_data
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "ok", 
                    "message": f"Сцена '{scene_data.scene_name}' обновлена", 
                    "updated": True
                }
            )
        else:
            # Новая сцена - обязательно нужен preview
            if not scene_data.preview_url:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": "Для новой сцены необходимо добавить превью"
                    }
                )
            
            scene = await SceneDAO.add_scene(
                user_id=user_id,
                scene_name=scene_data.scene_name,
                map_id=scene_data.map_id,
                objects=scene_data.objects,
                preview_url=scene_data.preview_url
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "ok", 
                    "message": f"Сцена '{scene_data.scene_name}' сохранена", 
                    "id": scene.id, 
                    "updated": False
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )
    
@router.get("/get_public_scenes/")
async def get_public_scenes(skip: int = 0, limit: int = 6):
    scenes, total = await SceneDAO.find_paginated_all(skip, limit)
    return {
        "items": [
            {
                "id": s.id,
                "title": s.scene_name,
                "preview": s.preview_url
            }
            for s in scenes
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/get_scene/{scene_id}/")
async def get_scene(scene_id: int):
    scene = await SceneDAO.find_scene(scene_id)
    if not scene:
        return JSONResponse(status_code=404, content={"detail": "Scene not found"})
    
    return {
        "id": scene.id,
        "map_id": scene.map_id,
        "objects": scene.objects,
        "scene_name": scene.scene_name
    }
