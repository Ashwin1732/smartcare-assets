from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database import get_db
from app.models.asset import Asset, AssetStatus

router = APIRouter()

LOW_BATTERY_THRESHOLD = 20.0


class TelemetryUpdate(BaseModel):
    tracking_id: str
    battery_level: float
    location: str


class TelemetryResponse(BaseModel):
    asset_code: str
    battery_level: float
    status: AssetStatus
    low_battery_alert: bool


@router.post("/telemetry", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.tracking_id == payload.tracking_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="No asset registered with this tracking ID")

    asset.battery_level = payload.battery_level
    asset.last_location = payload.location
    asset.last_updated = datetime.utcnow()

    low_battery = payload.battery_level < LOW_BATTERY_THRESHOLD
    if low_battery:
        asset.status = AssetStatus.MAINTENANCE_REQUIRED

    await db.commit()
    await db.refresh(asset)

    return TelemetryResponse(
        asset_code=asset.asset_code,
        battery_level=asset.battery_level,
        status=asset.status,
        low_battery_alert=low_battery,
    )
