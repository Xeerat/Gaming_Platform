from app.dao.base import BaseDAO
from app.friends.models import Friend_Request, Friends

 
class Friend_RequestDAO(BaseDAO):
    model = Friend_Request

class FriendsDAO(BaseDAO):
    model = Friends