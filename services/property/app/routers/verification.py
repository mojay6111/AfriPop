from fastapi import APIRouter

router = APIRouter()


@router.post("/{property_id}/verify")
async def verify_property(property_id: str):
    return {"message": "verification endpoint coming soon"}
