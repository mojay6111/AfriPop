from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.property import Property, PropertyImage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import imagehash


PHASH_THRESHOLD = 10
DESCRIPTION_THRESHOLD = 0.85


async def check_duplicate_images(phash: str, db: AsyncSession) -> bool:
    result = await db.execute(select(PropertyImage.phash).where(PropertyImage.phash != None))
    existing_hashes = result.scalars().all()
    new_hash = imagehash.hex_to_hash(phash)
    for existing in existing_hashes:
        try:
            diff = new_hash - imagehash.hex_to_hash(existing)
            if diff < PHASH_THRESHOLD:
                return True
        except Exception:
            continue
    return False


async def check_duplicate_description(description: str, db: AsyncSession) -> bool:
    if not description or len(description) < 50:
        return False
    result = await db.execute(
        select(Property.description).where(Property.description != None)
    )
    existing = result.scalars().all()
    if not existing:
        return False
    corpus = existing + [description]
    vectorizer = TfidfVectorizer().fit_transform(corpus)
    similarity = cosine_similarity(vectorizer[-1], vectorizer[:-1])
    return float(similarity.max()) > DESCRIPTION_THRESHOLD


async def run_fraud_checks(
    property_id: str,
    description: str,
    image_phashes: list[str],
    db: AsyncSession,
) -> list[str]:
    flags = []
    for phash in image_phashes:
        if await check_duplicate_images(phash, db):
            flags.append("duplicate_image")
            break
    if await check_duplicate_description(description, db):
        flags.append("duplicate_description")
    return flags
