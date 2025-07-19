from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.reply_model import Reply
from app.models.user_model import User
from app.models.discussion_model import Discussion
from app.schemas.reply_schema import (
    ReplyCreate,
    ReplyUpdate,
    ReplyResponse,
    ReplyListResponse,
)


class ReplyService:
    @staticmethod
    def create_reply(db: Session, reply_data: ReplyCreate, user_id: int) -> ReplyResponse:
        """Create a new reply"""
        # Verify discussion exists
        discussion = db.query(Discussion).filter(Discussion.id == reply_data.discussion_id).first()
        if not discussion:
            raise ValueError("Discussion not found")
        
        db_reply = Reply(
            content=reply_data.content,
            discussion_id=reply_data.discussion_id,
            user_id=user_id,
        )
        db.add(db_reply)
        db.commit()
        db.refresh(db_reply)
        
        # Get the author username
        author = db.query(User).filter(User.id == user_id).first()
        
        return ReplyResponse(
            id=db_reply.id,
            content=db_reply.content,
            discussion_id=db_reply.discussion_id,
            user_id=db_reply.user_id,
            author=author.username if author else "Unknown",
            created_at=db_reply.created_at,
            updated_at=db_reply.updated_at,
        )

    @staticmethod
    def get_replies_by_discussion(db: Session, discussion_id: int) -> ReplyListResponse:
        """Get all replies for a specific discussion"""
        # Verify discussion exists
        discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
        if not discussion:
            raise ValueError("Discussion not found")
        
        replies = db.query(Reply).options(joinedload(Reply.user)).filter(
            Reply.discussion_id == discussion_id
        ).order_by(Reply.created_at.asc()).all()
        
        reply_responses = []
        for reply in replies:
            reply_responses.append(
                ReplyResponse(
                    id=reply.id,
                    content=reply.content,
                    discussion_id=reply.discussion_id,
                    user_id=reply.user_id,
                    author=reply.user.username if reply.user else "Unknown",
                    created_at=reply.created_at,
                    updated_at=reply.updated_at,
                )
            )
        
        return ReplyListResponse(
            replies=reply_responses,
            total=len(reply_responses),
        )

    @staticmethod
    def update_reply(
        db: Session, reply_id: int, reply_data: ReplyUpdate, user_id: int
    ) -> Optional[ReplyResponse]:
        """Update a reply (only by the author)"""
        reply = db.query(Reply).filter(
            Reply.id == reply_id,
            Reply.user_id == user_id
        ).first()
        
        if not reply:
            return None
        
        # Update content
        if reply_data.content is not None:
            reply.content = reply_data.content
        
        db.commit()
        db.refresh(reply)
        
        # Get the author username
        author = db.query(User).filter(User.id == user_id).first()
        
        return ReplyResponse(
            id=reply.id,
            content=reply.content,
            discussion_id=reply.discussion_id,
            user_id=reply.user_id,
            author=author.username if author else "Unknown",
            created_at=reply.created_at,
            updated_at=reply.updated_at,
        )

    @staticmethod
    def delete_reply(db: Session, reply_id: int, user_id: int) -> bool:
        """Delete a reply (only by the author)"""
        reply = db.query(Reply).filter(
            Reply.id == reply_id,
            Reply.user_id == user_id
        ).first()
        
        if not reply:
            return False
        
        db.delete(reply)
        db.commit()
        return True 