from fastapi import FastAPI

from app.routers import assets, telemetry

app = FastAPI(
    title="SmartCare Assets API",
    description="Intelligent Hospital Asset Tracking and Equipment Management Platform",
    version="1.0.0",
)

app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
