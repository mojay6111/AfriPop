from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.property import (
    PropertyType, PropertyStatus, PricePeriod,
    FurnishingType, VerificationStatus, AmenityType
)


class AmenityOut(BaseModel):
    id: str
    amenity: AmenityType

    class Config:
        from_attributes = True


class ImageOut(BaseModel):
    id: str
    url: str
    is_primary: bool
    width: Optional[int]
    height: Optional[int]

    class Config:
        from_attributes = True


class PropertyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    property_type: PropertyType
    bedrooms: int = 0
    bathrooms: int = 1
    floor_area_sqm: Optional[float] = None
    furnishing: FurnishingType = FurnishingType.unfurnished
    price: float
    price_period: PricePeriod = PricePeriod.monthly
    currency: str = "KES"
    address: Optional[str] = None
    city: str
    neighbourhood: Optional[str] = None
    country: str = "Kenya"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    virtual_tour_url: Optional[str] = None
    amenities: Optional[List[AmenityType]] = []


class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor_area_sqm: Optional[float] = None
    furnishing: Optional[FurnishingType] = None
    price: Optional[float] = None
    price_period: Optional[PricePeriod] = None
    currency: Optional[str] = None
    address: Optional[str] = None
    neighbourhood: Optional[str] = None
    virtual_tour_url: Optional[str] = None
    amenities: Optional[List[AmenityType]] = None


class PropertyStatusUpdate(BaseModel):
    status: PropertyStatus


class PropertyOut(BaseModel):
    id: str
    landlord_id: str
    title: str
    description: Optional[str]
    property_type: PropertyType
    status: PropertyStatus
    bedrooms: int
    bathrooms: int
    floor_area_sqm: Optional[float]
    furnishing: FurnishingType
    price: float
    price_period: PricePeriod
    currency: str
    address: Optional[str]
    city: str
    neighbourhood: Optional[str]
    country: str
    latitude: Optional[float]
    longitude: Optional[float]
    verification_status: VerificationStatus
    needs_review: bool
    is_featured: bool
    view_count: int
    virtual_tour_url: Optional[str]
    created_at: datetime
    images: List[ImageOut] = []
    amenities: List[AmenityOut] = []

    class Config:
        from_attributes = True


class PropertyListOut(BaseModel):
    total: int
    page: int
    limit: int
    results: List[PropertyOut]


class NearbyResult(BaseModel):
    property: PropertyOut
    distance_km: float
