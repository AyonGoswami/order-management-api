from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from services.order_service import (
    create_order, get_orders_for_user, get_order_by_id,
    update_order_status, delete_order,
)
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
def place_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items_list = [item.model_dump() for item in data.items]
    order = create_order(db, current_user.id, items_list, data.currency)
    return order


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orders = get_orders_for_user(db, current_user.id)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = get_order_by_id(db, order_id, current_user.id)
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = update_order_status(db, order_id, current_user.id, data.status)
    return order


@router.delete("/{order_id}")
def remove_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = delete_order(db, order_id, current_user.id)
    return result
