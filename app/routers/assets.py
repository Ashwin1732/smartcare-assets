from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models.asset import Asset, AssetStatus

router = APIRouter()


class AssetCreate(BaseModel):
    asset_code: str
    equipment_type: str
    department: str
    tracking_id: str


class AssetOut(BaseModel):
    asset_code: str
    equipment_type: str
    department: str
    tracking_id: str
    status: AssetStatus
    battery_level: float | None
    last_location: str | None

    class Config:
        from_attributes = True


@router.post("/", response_model=AssetOut)
async def register_asset(payload: AssetCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Asset).where(Asset.tracking_id == payload.tracking_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tracking ID already assigned to another asset")

    asset = Asset(**payload.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/search", response_model=list[AssetOut])
async def search_assets(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Asset).where(Asset.asset_code.ilike(f"%{q}%") | Asset.equipment_type.ilike(f"%{q}%"))
    )
    return result.scalars().all()
