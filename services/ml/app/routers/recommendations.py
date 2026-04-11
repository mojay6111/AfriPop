from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class RecommendRequest(BaseModel):
    property_id: str
    city: str
    property_type: str
    price: float
    bedrooms: int
    amenity_count: int = 3
    limit: int = 5


class RecommendResponse(BaseModel):
    property_id: str
    match_score: float
    reason: str


@router.post("/recommend")
async def recommend(req: RecommendRequest):
    return {
        "property_id": req.property_id,
        "message": "Content-based recommendations served by property service",
        "note": "Collaborative filtering available after real user interaction data collected",
        "model_version": "content_based_v1",
    }
