import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Order, OrderItem, OrderStatus, Product


def create_order(db: Session, user_id: int, items_data: list[dict], currency: str) -> Order:
    if not items_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your order must have at least one item. Please add an item!",
        )

    order_number = "ORD-" + uuid.uuid4().hex[:8].upper()

    order = Order(
        order_number=order_number,
        user_id=user_id,
        status=OrderStatus.PLACED,
        total_amount=0.0,
        currency=currency,
    )
    db.add(order)
    db.flush()

    total = 0.0

    for item in items_data:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()

        if not product:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item['product_id']} is not found...",
            )

        if not product.is_active:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not active",
            )

        if product.stock < item["quantity"]:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{product.name} is out of stock'. Available: {product.stock}, Requested: {item['quantity']}",
            )

        line_total = product.price * item["quantity"]

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            sku_snapshot=product.sku,
            unit_price_snapshot=product.price,
            quantity=item["quantity"],
            line_total=line_total,
        )
        db.add(order_item)

        product.stock -= item["quantity"]
        total += line_total

    order.total_amount = round(total, 2)
    db.commit()
    db.refresh(order)
    return order


def get_orders_for_user(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_order_by_id(db: Session, order_id: int, user_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found...",
        )
    return order


def update_order_status(db: Session, order_id: int, user_id: int, new_status: str) -> Order:
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    valid_statuses = [s.value for s in OrderStatus]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    allowed_transitions = {
        "placed": ["paid", "cancelled"],
        "paid": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": [],
    }

    current = order.status.value
    if new_status not in allowed_transitions.get(current, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from '{current}' to '{new_status}'",
        )

    if new_status == "cancelled" and current in ["placed", "paid"]:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity

    order.status = OrderStatus(new_status)
    order.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int, user_id: int):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    if order.status.value not in ["placed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only delete orders which are either PLACED or CANCELLED!",
        )

    if order.status.value == "placed":
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity

    db.delete(order)
    db.commit()
    return {"message": "Order has been sucessfully deleted."}
