from backend import models

def create_restaurant(db, data):
    r = models.Restaurant(**data.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def get_restaurants(db, cuisine=None):
    query = db.query(models.Restaurant)
    if cuisine:
        query = query.filter(models.Restaurant.cuisine == cuisine)
    return query.all()


def create_menu_item(db, data):
    m = models.MenuItem(**data.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def create_order(db, data):
    order = models.Order(
        user_id=data.user_id,
        status="placed",
        payment_status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders(db, user_id):
    return db.query(models.Order)\
             .filter(models.Order.user_id == user_id)\
             .all()