from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
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
    def create_discussion(db: Session, discussion_data: DiscussionCreate, user_id: int) -> DiscussionResponse:
        """Create a new discussion"""
        db_discussion = Discussion(
            title=discussion_data.title,
            content=discussion_data.content,
            category=discussion_data.category,
            user_id=user_id,
        )
        db.add(db_discussion)
        db.commit()
        db.refresh(db_discussion)
        
        # Get the author username
        author = db.query(User).filter(User.id == user_id).first()
        
        return DiscussionResponse(
            id=db_discussion.id,
            title=db_discussion.title,
            content=db_discussion.content,
            category=db_discussion.category,
            user_id=db_discussion.user_id,
            author=author.username if author else "Unknown",
            replies_count=0,
            created_at=db_discussion.created_at,
            updated_at=db_discussion.updated_at,
        )

    @staticmethod
    def get_discussions(
        db: Session, filters: DiscussionFilters
    ) -> DiscussionListResponse:
        """Get discussions with filters and pagination"""
        query = db.query(Discussion).options(joinedload(Discussion.user))
        
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
        total = query.count()
        
        # Apply sorting
        if filters.sort_by == "oldest":
            query = query.order_by(asc(Discussion.created_at))
        elif filters.sort_by == "most-replies":
            query = query.outerjoin(Reply).group_by(Discussion.id).order_by(
                desc(func.count(Reply.id))
            )
        else:  # newest (default)
            query = query.order_by(desc(Discussion.created_at))
        
        # Apply pagination
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)
        
        discussions = query.all()
        
        # Convert to response format
        discussion_responses = []
        for discussion in discussions:
            replies_count = db.query(Reply).filter(Reply.discussion_id == discussion.id).count()
            discussion_responses.append(
                DiscussionResponse(
                    id=discussion.id,
                    title=discussion.title,
                    content=discussion.content,
                    category=discussion.category,
                    user_id=discussion.user_id,
                    author=discussion.user.username if discussion.user else "Unknown",
                    replies_count=replies_count,
                    created_at=discussion.created_at,
                    updated_at=discussion.updated_at,
                )
            )
        
        total_pages = (total + filters.limit - 1) // filters.limit
        
        return DiscussionListResponse(
            discussions=discussion_responses,
            total=total,
            page=filters.page,
            total_pages=total_pages,
        )

    @staticmethod
    def get_discussion(db: Session, discussion_id: int) -> Optional[DiscussionResponse]:
        """Get a specific discussion by ID"""
        discussion = db.query(Discussion).options(joinedload(Discussion.user)).filter(
            Discussion.id == discussion_id
        ).first()
        
        if not discussion:
            return None
        
        replies_count = db.query(Reply).filter(Reply.discussion_id == discussion.id).count()
        
        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            category=discussion.category,
            user_id=discussion.user_id,
            author=discussion.user.username if discussion.user else "Unknown",
            replies_count=replies_count,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )

    @staticmethod
    def update_discussion(
        db: Session, discussion_id: int, discussion_data: DiscussionUpdate, user_id: int
    ) -> Optional[DiscussionResponse]:
        """Update a discussion (only by the author)"""
        discussion = db.query(Discussion).filter(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id
        ).first()
        
        if not discussion:
            return None
        
        # Update fields
        if discussion_data.title is not None:
            discussion.title = discussion_data.title
        if discussion_data.content is not None:
            discussion.content = discussion_data.content
        if discussion_data.category is not None:
            discussion.category = discussion_data.category
        
        db.commit()
        db.refresh(discussion)
        
        # Get the author username
        author = db.query(User).filter(User.id == user_id).first()
        replies_count = db.query(Reply).filter(Reply.discussion_id == discussion.id).count()
        
        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            category=discussion.category,
            user_id=discussion.user_id,
            author=author.username if author else "Unknown",
            replies_count=replies_count,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )

    @staticmethod
    def delete_discussion(db: Session, discussion_id: int, user_id: int) -> bool:
        """Delete a discussion (only by the author)"""
        discussion = db.query(Discussion).filter(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id
        ).first()
        
        if not discussion:
            return False
        
        db.delete(discussion)
        db.commit()
        return True 