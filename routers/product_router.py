from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProductCreate, ProductUpdate, ProductResponse, SuggestMetadataRequest, SuggestMetadataResponse
from services.product_service import (
    create_product, get_all_products, get_product_by_id,
    update_product, delete_product, suggest_metadata,
)
from dependencies import get_current_user, require_admin
from models import User


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create(
    data: ProductCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = create_product(db, data.model_dump())
    return product


@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    products = get_all_products(db, skip, limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = update_product(db, product_id, data.model_dump(exclude_unset=True))
    return product


@router.delete("/{product_id}")
def delete(
    product_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = delete_product(db, product_id)
    return result


@router.post("/suggest-metadata", response_model=SuggestMetadataResponse)
def suggest(
    data: SuggestMetadataRequest,
    current_user: User = Depends(require_admin),
):
    result = suggest_metadata(data.product_name)
    return result
