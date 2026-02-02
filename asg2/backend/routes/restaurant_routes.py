from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models

router = APIRouter()


@router.post("/restaurants")
def create_restaurant(
    name: str,
    cuisine: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).get(user_id)
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    restaurant = models.Restaurant(name=name, cuisine=cuisine)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.get("/restaurants")
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


@router.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"message": "Restaurant deleted"}
