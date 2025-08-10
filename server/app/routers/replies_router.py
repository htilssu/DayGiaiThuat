from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_db
from app.schemas.reply_schema import (
    ReplyCreate,
    ReplyUpdate,
    ReplyResponse,
    ReplyListResponse,
)
from app.services.reply_service import ReplyService
from app.utils.utils import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/replies", tags=["replies"])


@router.post("/", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_reply(
    reply_data: ReplyCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new reply"""
    try:
        return await ReplyService.create_reply(db, reply_data, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/discussion/{discussion_id}", response_model=ReplyListResponse)
async def get_replies_by_discussion(
    discussion_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get all replies for a specific discussion"""
    try:
        return await ReplyService.get_replies_by_discussion(db, discussion_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{reply_id}", response_model=ReplyResponse)
async def update_reply(
    reply_id: int,
    reply_data: ReplyUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Update a reply (only by the author)"""
    reply = await ReplyService.update_reply(db, reply_id, reply_data, current_user.id)
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply not found or you don't have permission to update it"
        )
    return reply


@router.delete("/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reply(
    reply_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a reply (only by the author)"""
    success = await ReplyService.delete_reply(db, reply_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply not found or you don't have permission to delete it"
        ) 