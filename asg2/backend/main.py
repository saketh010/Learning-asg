from fastapi import FastAPI
from backend.database import engine
from backend import models

from backend.routes import (
    auth_routes,
    restaurant_routes,
    menu_routes,
    cart_routes,
    order_routes,
    admin_routes
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(menu_routes.router)
app.include_router(cart_routes.router)
app.include_router(order_routes.router)
app.include_router(admin_routes.router)
