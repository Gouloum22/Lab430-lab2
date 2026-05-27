"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from collections import defaultdict
from types import SimpleNamespace

from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders from Redis"""
    r = get_redis_conn()
    orders_in_redis = r.keys("order:*")
    orders = []

    for key in orders_in_redis:
        order_data = r.hgetall(key)

        decoded_order = {}
        for field, value in order_data.items():
            field = field.decode("utf-8") if isinstance(field, bytes) else field
            value = value.decode("utf-8") if isinstance(value, bytes) else value
            decoded_order[field] = value

        orders.append(SimpleNamespace(
            id=int(decoded_order["id"]),
            user_id=int(decoded_order["user_id"]),
            total_amount=float(decoded_order["total_amount"])
        ))

    orders = sorted(orders, key=lambda order: order.id, reverse=True)

    return orders[:limit]

def get_highest_spending_users(top_n=10):
    """Return top N users who spent the most"""
    r = get_redis_conn()
    orders_in_redis = r.keys("order:*")

    expenses_by_user = defaultdict(float)

    for key in orders_in_redis:
        order_data = r.hgetall(key)

        decoded_order = {}
        for field, value in order_data.items():
            field = field.decode("utf-8") if isinstance(field, bytes) else field
            value = value.decode("utf-8") if isinstance(value, bytes) else value
            decoded_order[field] = value

        user_id = int(decoded_order["user_id"])
        total_amount = float(decoded_order["total_amount"])

        expenses_by_user[user_id] += total_amount

    highest_spending_users = sorted(
        expenses_by_user.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return highest_spending_users[:top_n]


def get_best_selling_products(limit=10):
    """Get best selling products from Redis"""
    r = get_redis_conn()
    product_keys = r.keys("product:*")
    products_sold = []

    for key in product_keys:
        quantity = r.get(key)

        key = key.decode("utf-8") if isinstance(key, bytes) else key
        quantity = quantity.decode("utf-8") if isinstance(quantity, bytes) else quantity

        product_id = int(key.split(":")[1])

        products_sold.append({
            "product_id": product_id,
            "quantity_sold": int(quantity)
        })

    products_sold = sorted(
        products_sold,
        key=lambda product: product["quantity_sold"],
        reverse=True
    )

    return products_sold[:limit]