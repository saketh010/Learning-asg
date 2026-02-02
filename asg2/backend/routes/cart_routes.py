from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models

router = APIRouter()


@router.post("/cart/add")
def add_to_cart(
    user_id: int,
    menu_item_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    menu = db.query(models.MenuItem).get(menu_item_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu item not found")

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


@router.get("/cart/{user_id}")
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter_by(user_id=user_id).all()

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


@router.post("/cart/update")
def update_cart_item(
    cart_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):
    cart_item = db.query(models.CartItem).get(cart_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = quantity

    db.commit()
    return {"message": "Cart updated"}


@router.delete("/cart/{cart_id}")
def delete_cart_item(cart_id: int, db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).get(cart_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item deleted"}
