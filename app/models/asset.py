import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AssetStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE_REQUIRED = "maintenance_required"
    OUT_OF_SERVICE = "out_of_service"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_code = Column(String, unique=True, nullable=False, index=True)
    equipment_type = Column(String, nullable=False)
    department = Column(String, nullable=False)
    tracking_id = Column(String, unique=True, nullable=False)
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE)
    battery_level = Column(Float, nullable=True)
    last_location = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
