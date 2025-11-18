
from fastapi import FastAPI

from app.users.router import router as router_users
from app.friends.router import router as router_friend_req

app = FastAPI()

app.include_router(router_users)
app.include_router(router_friend_req)
