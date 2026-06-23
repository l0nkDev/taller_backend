from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

from database import engine

from models.category import Category
from models.dish_price import DishPrice
from models.dish_cost import DishCost
from models.dish import Dish
from models.floor import Floor
from models.order_detail import OrderDetail
from models.order import Order
from models.payment import Payment
from models.table_group import TableGroup
from models.table import Table
from models.user import User
from models.wall import Wall


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Tu Café API",
    description="Backend services for Tu Cafe",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import (
    auth_router,
    editor_router,
    floor_router,
    order_router,
    dish_router,
    category_router,
    user_router,
    bi_router,
    ai_router,
)

app.include_router(floor_router.router, prefix="/api/v1")
app.include_router(category_router.router, prefix="/api/v1")
app.include_router(dish_router.router, prefix="/api/v1")
app.include_router(order_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(user_router.router, prefix="/api/v1")
app.include_router(editor_router.router, prefix="/api/v1")
app.include_router(bi_router.router, prefix="/api/v1")
app.include_router(ai_router.router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Tu Café backend is running!"}
