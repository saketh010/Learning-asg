from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models

router = APIRouter()


@router.post("/orders/place")
def place_order(user_id: int, restaurant_id: int, db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter_by(user_id=user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart empty")

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


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if order.status == "delivered":
        raise HTTPException(status_code=400, detail="Cannot cancel delivered order")

    order.status = "cancelled"
    db.commit()
    return {"message": "Order cancelled"}


@router.get("/orders/history/{user_id}")
def order_history(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter_by(user_id=user_id).all()
    result = []

    for o in orders:
        items = db.query(models.OrderItem).filter_by(order_id=o.id).all()
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
                }
                for i in items
            ],
            "total_paid": total
        })

    return result
