from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import Depends
import datetime

router = APIRouter()


# -----------------------------
# Track Ad Events
# -----------------------------
@router.post("/track")
async def track_event(
    event: schemas.AdEventBase,
    db: Session = Depends(models.SessionLocal)
):
    """
    Endpoint to track ad events (impression or click)
    POST JSON:
    {
        "event_type": "impression" | "click",
        "website_id": 1
    }
    """
    # Validate event_type
    if event.event_type not in ["impression", "click"]:
        raise HTTPException(status_code=400, detail="Invalid event type")

    # Validate website
    website = db.query(models.Website).filter(models.Website.id == event.website_id).first()
    if not website or not website.is_verified:
        raise HTTPException(status_code=404, detail="Website not found or not verified")

    # Create AdEvent record
    ad_event = models.AdEvent(
        website_id=event.website_id,
        event_type=event.event_type,
        created_at=datetime.datetime.utcnow()
    )
    db.add(ad_event)
    db.commit()
    db.refresh(ad_event)

    return {
        "status": "success",
        "website_id": event.website_id,
        "event_type": event.event_type,
        "ad_event_id": ad_event.id
    }


# -----------------------------
# Helper: Get Stats for Dashboard
# -----------------------------
def get_website_stats(db: Session, website_id: int):
    impressions = db.query(models.AdEvent).filter(
        models.AdEvent.website_id == website_id,
        models.AdEvent.event_type == "impression"
    ).count()

    clicks = db.query(models.AdEvent).filter(
        models.AdEvent.website_id == website_id,
        models.AdEvent.event_type == "click"
    ).count()

    revenue = models.calculate_revenue(impressions, clicks)

    website = db.query(models.Website).filter(models.Website.id == website_id).first()
    if not website:
        return None

    return schemas.WebsiteStats(
        website_id=website.id,
        name=website.name,
        domain=website.domain,
        impressions=impressions,
        clicks=clicks,
        estimated_revenue=revenue
    )
