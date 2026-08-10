import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_asset_success(client):
    payload = {
        "asset_code": "V-102",
        "equipment_type": "Ventilator",
        "department": "ICU",
        "tracking_id": "BLE-90821",
    }
    response = await client.post("/api/v1/assets/", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["asset_code"] == "V-102"
    assert body["status"] == "available"


@pytest.mark.asyncio
async def test_register_asset_duplicate_tracking_id_rejected(client):
    payload = {
        "asset_code": "V-102",
        "equipment_type": "Ventilator",
        "department": "ICU",
        "tracking_id": "BLE-90821",
    }
    await client.post("/api/v1/assets/", json=payload)

    duplicate = {**payload, "asset_code": "V-103"}
    response = await client.post("/api/v1/assets/", json=duplicate)
    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"]


@pytest.mark.asyncio
async def test_telemetry_triggers_low_battery_alert(client):
    await client.post("/api/v1/assets/", json={
        "asset_code": "IP-42",
        "equipment_type": "Infusion Pump",
        "department": "ICU",
        "tracking_id": "BLE-55110",
    })

    response = await client.post("/api/v1/telemetry/telemetry", json={
        "tracking_id": "BLE-55110",
        "battery_level": 12.0,
        "location": "ICU Room 2",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["low_battery_alert"] is True
    assert body["status"] == "maintenance_required"


@pytest.mark.asyncio
async def test_telemetry_unknown_tracking_id_returns_404(client):
    response = await client.post("/api/v1/telemetry/telemetry", json={
        "tracking_id": "BLE-DOES-NOT-EXIST",
        "battery_level": 50.0,
        "location": "ICU Room 1",
    })
    assert response.status_code == 404
