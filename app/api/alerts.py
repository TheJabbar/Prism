from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from app.database.session import async_session_factory
from app.database.models import Alert
from sqlalchemy import select

router = APIRouter()


class AlertCreate(BaseModel):
    alert_type: str
    symbol: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    keyword: Optional[str] = None


@router.get("/")
async def list_alerts():
    async with async_session_factory() as session:
        result = await session.execute(select(Alert).where(Alert.is_active == True))
        alerts = result.scalars().all()
        return [
            {
                "id": a.id,
                "type": a.alert_type,
                "symbol": a.symbol,
                "condition": a.condition,
                "threshold": a.threshold,
                "keyword": a.keyword,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]


@router.post("/")
async def create_alert(data: AlertCreate):
    async with async_session_factory() as session:
        alert = Alert(
            alert_type=data.alert_type,
            symbol=data.symbol,
            condition=data.condition,
            threshold=data.threshold,
            keyword=data.keyword,
        )
        session.add(alert)
        await session.commit()
        return {"id": alert.id, "type": alert.alert_type}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    async with async_session_factory() as session:
        alert = await session.get(Alert, alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        alert.is_active = False
        await session.commit()
        return {"status": "deleted", "id": alert_id}
