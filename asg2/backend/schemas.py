from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class RestaurantCreate(BaseModel):
    name: str
    cuisine: str

class MenuItemCreate(BaseModel):
    name: str
    price: float
    restaurant_id: int

class OrderCreate(BaseModel):
    user_id: int