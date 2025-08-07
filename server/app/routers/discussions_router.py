from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_db
from app.schemas.discussion_schema import (
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionFilters,
    DiscussionResponse,
    DiscussionListResponse,
)
from app.services.discussion_service import DiscussionService
from app.utils.utils import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.post(
    "/", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED
)
async def create_discussion(
    discussion_data: DiscussionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new discussion"""
    return await DiscussionService.create_discussion(db, discussion_data, current_user.id)


@router.get("/", response_model=DiscussionListResponse)
async def get_discussions(
    search: Optional[str] = Query(None, description="Search in title and content"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: Optional[str] = Query(
        "newest", description="Sort by: newest, oldest, most-replies"
    ),
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_async_db),
):
    """Get discussions with filters and pagination"""
    filters = DiscussionFilters(
        search=search,
        category=category,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )
    return await DiscussionService.get_discussions(db, filters)


@router.get("/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific discussion by ID"""
    discussion = await DiscussionService.get_discussion(db, discussion_id)
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found"
        )
    return discussion


@router.patch("/{discussion_id}", response_model=DiscussionResponse)
async def update_discussion(
    discussion_id: int,
    discussion_data: DiscussionUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update a discussion (only by the author)"""
    discussion = await DiscussionService.update_discussion(
        db, discussion_id, discussion_data, current_user.id
    )
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found or you don't have permission to update it",
        )
    return discussion


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a discussion (only by the author)"""
    success = await DiscussionService.delete_discussion(db, discussion_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion not found or you don't have permission to delete it",
        )
