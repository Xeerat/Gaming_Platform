
from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.users.dao import UsersDAO
from app.friends.dao import Friend_RequestDAO, FriendsDAO
from app.users.models import User
from app.users.dependencies import get_current_user
from app.friends.schemas import SFriend_request

router = APIRouter(prefix='/friends', tags=['Friends'])

@router.post("/request/")
async def send_request(user_to_data: SFriend_request, user_from: User = Depends(get_current_user)):
    # Ищем пользователя, которому отправляют запрос
    user_to = await UsersDAO.find_one_or_none(username=user_to_data.username_to)
    if user_to is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователя не существует"
        )

    # нельзя кинуть запрос себе
    if user_from.id == user_to.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете отправить запрос самому себе"
        )

    # наличие такого запроса
    existing = await Friend_RequestDAO.find_one_or_none(
        from_user_id=user_from.id,
        to_user_id=user_to.id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Запрос дружбы уже был отправлен"
        )

    # Создаём заявку
    request_dict = {
        "from_user_id": user_from.id,
        "to_user_id": user_to.id
    }

    await Friend_RequestDAO.add(**request_dict)

    return {"message": "Запрос успешно отправлен"}

@router.post("/accept/")
async def accept_request(request_id : int, user : User = Depends(get_current_user)) :
    request = await Friend_RequestDAO.find_one_or_none(id=request_id, to_user_id=user.id)
    
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запроса не существует"
        )
    
    from_user_id = request.from_user_id
    to_user_id = request.to_user_id  
    
    await FriendsDAO.add(user_id=from_user_id, friend_id=to_user_id)
    await FriendsDAO.add(user_id=to_user_id, friend_id=from_user_id)

    await Friend_RequestDAO.delete(id=request_id)


@router.get("/all_friends/")
async def get_all_friends(user : User = Depends(get_current_user)) :
    friends = await FriendsDAO.find_all(user_id=user.id)

    return friends

@router.get("/sent_requests/")
async def get_sent_requests(user : User = Depends(get_current_user)) :
    requests = await Friend_RequestDAO.find_all(from_user_id=user.id)
    return requests

@router.get("/incoming_requests/")
async def get_incoming_requests(user : User = Depends(get_current_user)) :
    requests = await Friend_RequestDAO.find_all(to_user_id=user.id)
    return requests

@router.delete("/dell/")
async def dell_request(user_to_data: SFriend_request, user_from_data: User = Depends(get_current_user)):
    user_to = await UsersDAO.find_one_or_none(username=user_to_data.username_to)
    check = await Friend_RequestDAO.delete(from_user_id=user_from_data.id, to_user_id=user_to.id)
    if check:
        return {"message": f"Запрос удален!"}
    else:
        return {"message": "Ошибка при удалении запроса"}


@router.delete("/decline/")
async def decline_request(request_id : int, user : User = Depends(get_current_user)):
    await Friend_RequestDAO.delete(id=request_id, to_user_id=user.id)

@router.delete("/del_friend/")
async def dell_friend(friendname: SFriend_request, user: User = Depends(get_current_user)) :
    friend = await UsersDAO.find_one_or_none(username=friendname.username_to)
    if not friend:
        raise HTTPException(status_code=404, detail="Такой друг не найден")
    
    await FriendsDAO.delete(user_id=user.id, friend_id=friend.id)
    await FriendsDAO.delete(user_id=friend.id, friend_id=user.id)

    return {"message": f"{friend.username} удален из друзей."}