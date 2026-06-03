import json
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from models import Product

logger = logging.getLogger("order_management")


def create_product(db: Session, data: dict) -> Product:
    existing = db.query(Product).filter(Product.sku == data["sku"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{data['sku']}' already exists",
        )

    product = Product(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_all_products(db: Session, skip: int = 0, limit: int = 50) -> list[Product]:
    return db.query(Product).offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product is not found!",
        )
    return product


def update_product(db: Session, product_id: int, data: dict) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product is not found!",
        )

    for key, value in data.items():
        if value is not None:
            setattr(product, key, value)

    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product is not found!",
        )

    db.delete(product)
    db.commit()
    return {"message": "Product has been successfully deleted."}


def suggest_metadata(product_name: str) -> dict:
    try:
        return _call_llm_for_metadata(product_name)
    except Exception as e:
        logger.warning(f"LLM call failed ({e}), using fallback metadata generator")
        return _fallback_metadata(product_name)


def _call_llm_for_metadata(product_name: str) -> dict:
    if not HTTPX_AVAILABLE:
        raise RuntimeError("httpx not installed")

    import os
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    prompt = (
        f"You are an intelligent product catalog assistant. Based on the product name provided, "
        f"generate ONLY a JSON object containing three keys:\n"
        f'  "description": a concise, professional 2-sentence summary of the product,\n'
        f'  "tags": a list of 3 relevant SEO keywords,\n'
        f'  "category": the most appropriate product category.\n\n'
        f"Product name: {product_name}\n\n"
        f"Return strictly the JSON object without any additional text."
    )

    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(f"OpenAI API returned {response.status_code}")

    content = response.json()["choices"][0]["message"]["content"]
    content = content.strip().strip("```json").strip("```").strip()
    result = json.loads(content)
    return {
        "description": result.get("description", ""),
        "tags": result.get("tags", []),
        "category": result.get("category", ""),
    }


def _fallback_metadata(product_name: str) -> dict:
    name_lower = product_name.lower()
    words = product_name.strip().split()

    category_map = {
        "Nike": "Clothing > Footwear > Shoes",
        "Adidas": "Clothing > Footwear > Shoes",
        "Puma": "Clothing > Footwear > Shoes",
        "Reebok": "Clothing > Footwear > Shoes",
        "Titan": "Accessories > Watches",
        "Rado": "Accessories > Watches",
        "Police": "Accessories > Watches",
        "Armani": "Accessories > Watches",
        "tablet": "Electronics > Tablets",
        "iPad": "Electronics > Tablets",
        "speaker": "Electronics > Computer Accessories",
        "Keyboard": "Electronics > Computer Accessories",
        "bag": "Accessories > Bags"
    }

    category = "lifestyle"
    for keyword, cat in category_map.items():
        if keyword in name_lower:
            category = cat
            break

    tags = [w.lower() for w in words if len(w) > 2]
    tags.append("best-seller")
    tags.append(category.split(" > ")[0].lower())
    tags = list(dict.fromkeys(tags))[:5]

    description = (
        f"High-quality {product_name} designed to meet and cater to your needs. "
        f"This product offers an excellent value and performance in the {category.split(' > ')[0]} category."
    )

    return {
        "description": description,
        "tags": tags,
        "category": category,
    }
