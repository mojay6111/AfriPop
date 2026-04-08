import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, DateTime, Enum as SAEnum,
    Float, Integer, Text, ForeignKey, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class PropertyType(str, enum.Enum):
    apartment = "apartment"
    house = "house"
    land = "land"
    commercial = "commercial"
    bedsitter = "bedsitter"


class PropertyStatus(str, enum.Enum):
    available = "available"
    rented = "rented"
    sold = "sold"
    under_offer = "under_offer"


class PricePeriod(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"
    once = "once"


class FurnishingType(str, enum.Enum):
    furnished = "furnished"
    semi_furnished = "semi_furnished"
    unfurnished = "unfurnished"


class VerificationStatus(str, enum.Enum):
    unverified = "unverified"
    pending_review = "pending_review"
    verified = "verified"
    rejected = "rejected"


class AmenityType(str, enum.Enum):
    wifi = "wifi"
    parking = "parking"
    pool = "pool"
    gym = "gym"
    security = "security"
    water = "water"
    electricity = "electricity"
    generator = "generator"
    borehole = "borehole"
    cctv = "cctv"
    furnished = "furnished"
    pet_friendly = "pet_friendly"
    balcony = "balcony"


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    landlord_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    property_type: Mapped[PropertyType] = mapped_column(SAEnum(PropertyType), nullable=False)
    status: Mapped[PropertyStatus] = mapped_column(SAEnum(PropertyStatus), default=PropertyStatus.available)
    bedrooms: Mapped[int] = mapped_column(Integer, default=0)
    bathrooms: Mapped[int] = mapped_column(Integer, default=1)
    floor_area_sqm: Mapped[float] = mapped_column(Float, nullable=True)
    furnishing: Mapped[FurnishingType] = mapped_column(SAEnum(FurnishingType), default=FurnishingType.unfurnished)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    price_period: Mapped[PricePeriod] = mapped_column(SAEnum(PricePeriod), default=PricePeriod.monthly)
    currency: Mapped[str] = mapped_column(String(10), default="KES")
    address: Mapped[str] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False, index=True)
    neighbourhood: Mapped[str] = mapped_column(String, nullable=True, index=True)
    country: Mapped[str] = mapped_column(String, default="Kenya")
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SAEnum(VerificationStatus), default=VerificationStatus.unverified
    )
    fraud_flags: Mapped[str] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    virtual_tour_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images: Mapped[list["PropertyImage"]] = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    amenities: Mapped[list["PropertyAmenity"]] = relationship("PropertyAmenity", back_populates="property", cascade="all, delete-orphan")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    phash: Mapped[str] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    property: Mapped["Property"] = relationship("Property", back_populates="images")


class PropertyAmenity(Base):
    __tablename__ = "property_amenities"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id: Mapped[str] = mapped_column(String, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    amenity: Mapped[AmenityType] = mapped_column(SAEnum(AmenityType), nullable=False)

    property: Mapped["Property"] = relationship("Property", back_populates="amenities")
