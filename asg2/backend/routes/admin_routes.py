from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models

router = APIRouter()

@router.get("/admin/orders")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    result = []

    for o in orders:
        items = db.query(models.OrderItem).filter_by(order_id=o.id).all()
        total = sum(i.price * i.quantity for i in items)

        result.append({
            "order_id": o.id,
            "user_id": o.user_id,
            "restaurant_name": o.restaurant_name,
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
            "total_amount": total
        })

    return result

@router.post("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    order.status = status
    db.commit()
    return {"message": "Status updated"}


@router.post("/orders/{order_id}/payment")
def update_payment_status(order_id: int, payment_status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    order.payment_status = payment_status
    db.commit()
    return {"message": "Payment updated"}
