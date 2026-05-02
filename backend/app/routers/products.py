import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import TrackedProduct
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TrackedProduct).order_by(TrackedProduct.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = TrackedProduct(**body.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    p = await db.get(TrackedProduct, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(product_id: uuid.UUID, body: ProductUpdate, db: AsyncSession = Depends(get_db)):
    p = await db.get(TrackedProduct, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(p, field, val)
    await db.flush()
    await db.refresh(p)
    return p


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    p = await db.get(TrackedProduct, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(p)
