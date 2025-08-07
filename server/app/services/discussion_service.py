from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, asc, select
from sqlalchemy.orm import joinedload

from app.models.discussion_model import Discussion
from app.models.user_model import User
from app.models.reply_model import Reply
from app.schemas.discussion_schema import (
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionFilters,
    DiscussionResponse,
    DiscussionListResponse,
)


class DiscussionService:
    @staticmethod
    async def create_discussion(db: AsyncSession, discussion_data: DiscussionCreate, user_id: int) -> DiscussionResponse:
        """Create a new discussion"""
        db_discussion = Discussion(
            title=discussion_data.title,
            content=discussion_data.content,
            category=discussion_data.category,
            user_id=user_id,
        )
        db.add(db_discussion)
        await db.commit()
        await db.refresh(db_discussion)
        
        # Get the author username
        result = await db.execute(select(User).filter(User.id == user_id))
        author = result.scalars().first()
        
        return DiscussionResponse(
            id=db_discussion.id,
            title=db_discussion.title,
            content=db_discussion.content,
            category=db_discussion.category,
            author=author.username if author else "Unknown",
            replies=0,
            createdAt=db_discussion.created_at.isoformat() if db_discussion.created_at else "",
            updatedAt=db_discussion.updated_at.isoformat() if db_discussion.updated_at else "",
        )

    @staticmethod
    async def get_discussions(
        db: AsyncSession, filters: DiscussionFilters
    ) -> DiscussionListResponse:
        """Get discussions with filters and pagination"""
        query = select(Discussion).options(joinedload(Discussion.user))
        
        # Apply search filter
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                (Discussion.title.ilike(search_term)) |
                (Discussion.content.ilike(search_term))
            )
        
        # Apply category filter
        if filters.category:
            query = query.filter(Discussion.category == filters.category)
        
        # Get total count before applying pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        if filters.sort_by == "oldest":
            query = query.order_by(asc(Discussion.created_at))
        elif filters.sort_by == "most-replies":
            # For most-replies, we need a more complex query
            query = query.outerjoin(Reply).group_by(Discussion.id).order_by(
                desc(func.count(Reply.id))
            )
        else:  # newest (default)
            query = query.order_by(desc(Discussion.created_at))
        
        # Apply pagination
        page = filters.page or 1
        limit = filters.limit or 10
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        discussions = result.scalars().all()
        
        # Convert to response format
        discussion_responses = []
        for discussion in discussions:
            # Get replies count
            replies_query = select(func.count(Reply.id)).filter(Reply.discussion_id == discussion.id)
            replies_result = await db.execute(replies_query)
            replies_count = replies_result.scalar() or 0
            
            discussion_responses.append(
                DiscussionResponse(
                    id=discussion.id,
                    title=discussion.title,
                    content=discussion.content,
                    category=discussion.category,
                    author=discussion.user.username if discussion.user else "Unknown",
                    replies=replies_count,
                    createdAt=discussion.created_at.isoformat() if discussion.created_at else "",
                    updatedAt=discussion.updated_at.isoformat() if discussion.updated_at else "",
                )
            )
        
        return DiscussionListResponse(
            discussions=discussion_responses,
            total=total,
            page=page,
            totalPages=(total + limit - 1) // limit,
        )

    @staticmethod
    async def get_discussion(db: AsyncSession, discussion_id: int) -> Optional[DiscussionResponse]:
        """Get a specific discussion by ID"""
        result = await db.execute(select(Discussion).options(joinedload(Discussion.user)).filter(
            Discussion.id == discussion_id
        ))
        discussion = result.scalars().first()
        
        if not discussion:
            return None
        
        replies_result = await db.execute(select(func.count(Reply.id)).filter(Reply.discussion_id == discussion.id))
        replies_count = replies_result.scalar() or 0
        
        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            category=discussion.category,
            author=discussion.user.username if discussion.user else "Unknown",
            replies=replies_count,
            createdAt=discussion.created_at.isoformat() if discussion.created_at else "",
            updatedAt=discussion.updated_at.isoformat() if discussion.updated_at else "",
        )

    @staticmethod
    async def update_discussion(
        db: AsyncSession, discussion_id: int, discussion_data: DiscussionUpdate, user_id: int
    ) -> Optional[DiscussionResponse]:
        """Update a discussion (only by the author)"""
        result = await db.execute(select(Discussion).filter(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id
        ))
        discussion = result.scalars().first()
        
        if not discussion:
            return None
        
        # Update fields if provided
        if discussion_data.title is not None:
            discussion.title = discussion_data.title
        if discussion_data.content is not None:
            discussion.content = discussion_data.content
        if discussion_data.category is not None:
            discussion.category = discussion_data.category
        
        await db.commit()
        await db.refresh(discussion)
        
        # Get the author username
        author_result = await db.execute(select(User).filter(User.id == user_id))
        author = author_result.scalars().first()
        replies_result = await db.execute(select(func.count(Reply.id)).filter(Reply.discussion_id == discussion.id))
        replies_count = replies_result.scalar() or 0
        
        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            category=discussion.category,
            author=author.username if author else "Unknown",
            replies=replies_count,
            createdAt=discussion.created_at.isoformat() if discussion.created_at else "",
            updatedAt=discussion.updated_at.isoformat() if discussion.updated_at else "",
        )

    @staticmethod
    async def delete_discussion(db: AsyncSession, discussion_id: int, user_id: int) -> bool:
        """Delete a discussion (only by the author)"""
        result = await db.execute(select(Discussion).filter(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id
        ))
        discussion = result.scalars().first()
        
        if not discussion:
            return False
        
        await db.delete(discussion)
        await db.commit()
        return True 