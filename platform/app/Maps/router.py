
from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.dao.dao_models import UsersDAO, MapsDAO
from app.migration.models import User
from app.users.dependencies import get_current_user
from app.Maps.validation import SMaps

router = APIRouter(prefix='/map', tags=['Game_maps'])


@router.options("/add_map/")
async def options_add_map(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return {}



@router.post("/add_map/")
async def add_map(input_: SMaps, user: User = Depends(get_current_user)):
    print("Получено input_:", input_)
    print("Пользователь:", user)

    check = await MapsDAO.find_one_or_none(name=input_.map_name, user_id=user.id)

    if check :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уже существует карта с таким именем"
        )

    
    # Создаём заявку
    input_dict = {
        "user_id": user.id,
        "name" : input_.map_name,
        "matrix" : input_.matrix
    }

    await MapsDAO.add(**input_dict)
    return {"message": "Карта успешно загружена"}


@router.get("/all_user_maps_names/")
async def get_all_maps(user : User = Depends(get_current_user)) :
    maps = await MapsDAO.find_all(user_id=user.id)

    all_maps_name = [m.name for m in maps]

    return all_maps_name

@router.get("/get_map/")
async def get_map(map_name : str , user : User = Depends(get_current_user)) :
    map_ = await MapsDAO.find_one_or_none(name=map_name)

    if map_ is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Карты не существует"
        )

    return map_.matrix

@router.delete("/delete_map/")
async def delete_map(map_id : int, user : User = Depends(get_current_user)):
    deleted = await MapsDAO.delete(id=map_id, user_id=user.id)
    if deleted:
        return {"message": "Карта удалена"}
    else:
        raise HTTPException(status_code=404, detail="Карта не найдена")


@router.put("/change_map/")
async def update_map(new_map: SMaps, user: User = Depends(get_current_user)) -> dict:
    # Формируем фильтр по user_id и name карты
    filter_by = {"user_id": user.id, "name": new_map.map_name}

    check = await MapsDAO.update(
        filter_by=filter_by,
        matrix=new_map.matrix  # обновляемые поля передаются через **values
    )

    if check:
        return {"message": "Карта обновлена"}
    else:
        return {"message": "Ошибка при обновлении карты"}

    