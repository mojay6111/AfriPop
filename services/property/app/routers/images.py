from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.property import Property, PropertyImage
from app.services.image_service import process_and_upload, delete_image

router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024


@router.post("/{property_id}/images", status_code=status.HTTP_201_CREATED)
async def upload_image(
    property_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    count_result = await db.execute(
        select(func.count()).select_from(PropertyImage).where(PropertyImage.property_id == property_id)
    )
    if count_result.scalar() >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images per property")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP allowed")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large, max 5MB")

    meta = process_and_upload(file_bytes, file.filename)

    count_result2 = await db.execute(
        select(func.count()).select_from(PropertyImage).where(PropertyImage.property_id == property_id)
    )
    is_primary = count_result2.scalar() == 0

    image = PropertyImage(
        property_id=property_id,
        url=meta["url"],
        filename=meta["filename"],
        is_primary=is_primary,
        file_size=meta["file_size"],
        width=meta["width"],
        height=meta["height"],
        phash=meta["phash"],
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@router.delete("/{property_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_image(property_id: str, image_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PropertyImage).where(
            PropertyImage.id == image_id,
            PropertyImage.property_id == property_id
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    delete_image(image.filename)
    await db.delete(image)
    await db.commit()
