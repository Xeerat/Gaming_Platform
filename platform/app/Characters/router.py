
from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.dao.dao_models import UsersDAO, CharDAO
from app.migration.models import User
from app.users.dependencies import get_current_user
from app.Characters.validation import SChar

router = APIRouter(prefix='/char', tags=['Characters'])


@router.post("/add_char/")
async def add_char(input_: SChar, user: User = Depends(get_current_user)):
    print("Получено input_:", input_)
    print("Пользователь:", user)

    check = await CharDAO.find_one_or_none(name=input_.map_name, user_id=user.id)

    if check :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уже существует персонаж с таким именем"
        )

    
    # Создаём заявку
    input_dict = {
        "user_id": user.id,
        "name" : input_.map_name,
        "matrix" : input_.matrix
    }

    await CharDAO.add(**input_dict)
    return {"message": "Персонаж успешно загружен"}


@router.get("/all_user_chars_names/")
async def get_all_chars(user : User = Depends(get_current_user)) :
    chars = await CharDAO.find_all(user_id=user.id)

    all_char_name = [m.name for m in chars]

    return all_char_name

@router.get("/get_char/")
async def get_char(char_name : str , user : User = Depends(get_current_user)) :
    char_ = await CharDAO.find_one_or_none(name=char_name)

    if char_ is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Персонажа не существует"
        )

    return char_.matrix

@router.delete("/delete_char/")
async def delete_char(char_id : int, user : User = Depends(get_current_user)):
    deleted = await CharDAO.delete(id=char_id, user_id=user.id)
    if deleted:
        return {"message": "Персонаж удален"}
    else:
        raise HTTPException(status_code=404, detail="Персонаж не найден")


@router.put("/change_char/")
async def update_char(new_char: SChar, user: User = Depends(get_current_user)) -> dict:
    # Формируем фильтр по user_id и name карты
    filter_by = {"user_id": user.id, "name": new_char.char_name}

    check = await CharDAO.update(
        filter_by=filter_by,
        matrix=new_char.matrix  # обновляемые поля передаются через **values
    )

    if check:
        return {"message": "Персонаж обновлен"}
    else:
        return {"message": "Ошибка при обновлении персонажа"}

    