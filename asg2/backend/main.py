from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine
from backend.deps import get_db
from backend import models, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# autth
@app.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    role = "admin" if username == "admin" else "user"

    user = models.User(
        username=username,
        password=auth.hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "role": role,
        "token": auth.create_token(user.id)
    }


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()

    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "user_id": user.id,
        "role": user.role,
        "token": auth.create_token(user.id)
    }

# restaurant mng
@app.post("/restaurants")
def create_restaurant(
    name: str,
    cuisine: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).get(user_id)
    if user.role != "admin":
        raise HTTPException(403, "Admin only")

    restaurant = models.Restaurant(name=name, cuisine=cuisine)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@app.get("/restaurants")
def list_restaurants(
    search: str = None,
    cuisine: str = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Restaurant)
    if search:
        q = q.filter(models.Restaurant.name.contains(search))
    if cuisine:
        q = q.filter(models.Restaurant.cuisine.contains(cuisine))
    return q.all()


@app.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted"}

#menu mng

@app.post("/menu")
def add_menu_item(
    name: str,
    price: float,
    restaurant_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).get(user_id)
    if user.role != "admin":
        raise HTTPException(403, "Admin only")

    item = models.MenuItem(
        name=name,
        price=price,
        restaurant_id=restaurant_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/menu/{restaurant_id}")
def get_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(models.MenuItem).filter_by(
        restaurant_id=restaurant_id
    ).all()


@app.delete("/menu/{menu_item_id}")
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).get(menu_item_id)
    if not item:
        raise HTTPException(404, "Menu item not found")

    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted"}

#cart mng

@app.post("/cart/add")
def add_to_cart(
    user_id: int,
    menu_item_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    menu = db.query(models.MenuItem).get(menu_item_id)
    if not menu:
        raise HTTPException(404, "Menu item not found")

    restaurant = db.query(models.Restaurant).get(menu.restaurant_id)

    cart_item = models.CartItem(
        user_id=user_id,
        menu_item_id=menu.id,
        item_name=menu.name,
        price=menu.price,
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        quantity=quantity
    )

    db.add(cart_item)
    db.commit()

    return {"message": "Added to cart"}

@app.get("/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem)\
                   .filter_by(user_id=user_id).all()

    return [
        {
            "cart_id": c.id,
            "item_name": c.item_name,
            "restaurant_name": c.restaurant_name,
            "quantity": c.quantity,
            "price": c.price,
            "total": c.price * c.quantity,
            "restaurant_id": c.restaurant_id
        }
        for c in cart_items
    ]



@app.post("/cart/update")
def update_cart_item(
    cart_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    cart_item = db.query(models.CartItem).get(cart_id)
    if not cart_item:
        raise HTTPException(404, "Cart item not found")

    if quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.commit()
    return {"message": "Cart updated"}


@app.delete("/cart/{cart_id}")
def delete_cart_item(cart_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).get(cart_id)
    if not cart_item:
        raise HTTPException(404, "Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item deleted"}

#order mng
@app.post("/orders/place")
def place_order(user_id: int, restaurant_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem)\
                   .filter_by(user_id=user_id).all()

    if not cart_items:
        raise HTTPException(400, "Cart empty")

    order = models.Order(
        user_id=user_id,
        restaurant_id=cart_items[0].restaurant_id,
        restaurant_name=cart_items[0].restaurant_name
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for c in cart_items:
        db.add(models.OrderItem(
            order_id=order.id,
            menu_item_id=c.menu_item_id,
            item_name=c.item_name,
            price=c.price,
            quantity=c.quantity
        ))
        db.delete(c)

    db.commit()
    return {"order_id": order.id}


@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if order.status == "delivered":
        raise HTTPException(400, "Cannot cancel delivered order")

    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled"}


@app.get("/orders/history/{user_id}")
def order_history(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter_by(user_id=user_id).all()

    result = []

    for o in orders:
        items = db.query(models.OrderItem)\
                  .filter_by(order_id=o.id).all()

        total = sum(i.price * i.quantity for i in items)

        result.append({
            "order_id": o.id,
            "restaurant": o.restaurant_name,
            "status": o.status,
            "payment_status": o.payment_status,
            "items": [
                {
                    "item_name": i.item_name,
                    "quantity": i.quantity,
                    "price": i.price * i.quantity
                } for i in items
            ],
            "total_paid": total
        })

    return result

# admin order mng
@app.get("/admin/orders")
def get_all_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@app.post("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).get(order_id)
    order.status = status
    db.commit()
    return {"message": "Status updated"}


@app.post("/orders/{order_id}/payment")
def update_payment_status(
    order_id: int,
    payment_status: str,
    db: Session = Depends(get_db)
):
    order = db.query(models.Order).get(order_id)
    order.payment_status = payment_status
    db.commit()
    return {"message": "Payment updated"}
