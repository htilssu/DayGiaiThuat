from fastapi import APIRouter

router = APIRouter(prefix="/topics", tags=["topics"])


# TODO: Get all topics
@router.get("/")
async def get_topics():
    return {"message": "Hello, World!"}
