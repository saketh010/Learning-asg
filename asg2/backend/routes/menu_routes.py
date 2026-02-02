from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models

router = APIRouter()


@router.post("/menu")
def add_menu_item(
    name: str,
    price: float,
    restaurant_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).get(user_id)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    item = models.MenuItem(
        name=name,
        price=price,
        restaurant_id=restaurant_id
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/menu/{restaurant_id}")
def get_menu(restaurant_id: int, db: Session = Depends(get_db)):
    return db.query(models.MenuItem)\
             .filter_by(restaurant_id=restaurant_id)\
             .all()


@router.delete("/menu/{menu_item_id}")
def delete_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).get(menu_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(item)
    db.commit()
    return {"message": "Menu item deleted"}
