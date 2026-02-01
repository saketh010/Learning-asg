from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role=Column(String,default="user")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    cuisine = Column(String)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    menu_item_id = Column(Integer)
    item_name = Column(String)
    price = Column(Float)

    restaurant_id = Column(Integer)
    restaurant_name = Column(String)

    quantity = Column(Integer)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

    restaurant_id = Column(Integer)
    restaurant_name = Column(String)

    status = Column(String, default="placed")
    payment_status = Column(String, default="pending")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)

    menu_item_id = Column(Integer)
    item_name = Column(String)
    price = Column(Float)

    quantity = Column(Integer)