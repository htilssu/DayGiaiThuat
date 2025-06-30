from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.lesson_model import Lesson, LessonSection
from app.schemas.lesson_schema import (
    CreateLessonSchema, UpdateLessonSchema, LessonResponseSchema,
    GenerateLessonRequestSchema, LessonSectionSchema
)
from app.core.agents.lesson_generating_agent import LessonGeneratingAgent


class LessonService:
    def __init__(self, db: Session):
        self.db = db
        self.agent = LessonGeneratingAgent()
    
    def generate_lesson(self, request: GenerateLessonRequestSchema, topic_id: int, order: int) -> LessonResponseSchema:
        """
        Generate a lesson using the RAG AI agent.
        """
        # Generate lesson using the agent
        lesson_data = self.agent.act(request)
        
        # Update the generated lesson with proper topic_id and order
        lesson_data.topic_id = topic_id
        lesson_data.order = order
        
        # Create the lesson in database
        return self.create_lesson(lesson_data)
    
    def create_lesson(self, lesson_data: CreateLessonSchema) -> LessonResponseSchema:
        """
        Create a new lesson with sections.
        """
        # Create lesson
        lesson = Lesson(
            external_id=lesson_data.external_id,
            title=lesson_data.title,
            description=lesson_data.description,
            topic_id=lesson_data.topic_id,
            order=lesson_data.order,
            next_lesson_id=lesson_data.next_lesson_id,
            prev_lesson_id=lesson_data.prev_lesson_id
        )
        
        self.db.add(lesson)
        self.db.flush()  # Get the lesson ID
        
        # Create lesson sections
        for section_data in lesson_data.sections:
            section = LessonSection(
                lesson_id=lesson.id,
                type=section_data.type,
                content=section_data.content,
                order=section_data.order,
                options=section_data.options,
                answer=section_data.answer,
                explanation=section_data.explanation
            )
            self.db.add(section)
        
        self.db.commit()
        self.db.refresh(lesson)
        
        return LessonResponseSchema.model_validate(lesson)
    
    def get_lesson_by_id(self, lesson_id: int) -> Optional[LessonResponseSchema]:
        """
        Get a lesson by ID.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        lesson = self.db.execute(stmt).scalar_one_or_none()
        
        if not lesson:
            return None
        
        lesson_dict = lesson.__dict__.copy()
        lesson_dict['sections'] = [
            LessonSectionSchema.model_validate(section, from_attributes=True) for section in lesson.sections
        ]
        lesson_dict['exercises'] = [ex for ex in lesson.exercises]
        return LessonResponseSchema.model_validate(lesson_dict)
    
    def get_lesson_by_external_id(self, external_id: str) -> Optional[LessonResponseSchema]:
        """
        Get a lesson by external ID.
        """
        stmt = select(Lesson).where(Lesson.external_id == external_id)
        lesson = self.db.execute(stmt).scalar_one_or_none()
        
        if not lesson:
            return None
        
        lesson_dict = lesson.__dict__.copy()
        lesson_dict['sections'] = [
            LessonSectionSchema.model_validate(section, from_attributes=True) for section in lesson.sections
        ]
        lesson_dict['exercises'] = [ex for ex in lesson.exercises]
        return LessonResponseSchema.model_validate(lesson_dict)
    
    def get_lessons_by_topic(self, topic_id: int) -> List[LessonResponseSchema]:
        """
        Get all lessons for a topic.
        """
        stmt = select(Lesson).where(Lesson.topic_id == topic_id).order_by(Lesson.order)
        lessons = self.db.execute(stmt).scalars().all()
        lesson_responses = []
        for lesson in lessons:
            lesson_dict = lesson.__dict__.copy()
            lesson_dict['sections'] = [
                LessonSectionSchema.model_validate(section, from_attributes=True) for section in lesson.sections
            ]
            lesson_dict['exercises'] = [ex for ex in lesson.exercises]
            lesson_responses.append(LessonResponseSchema.model_validate(lesson_dict))
        return lesson_responses
    
    def update_lesson(self, lesson_id: int, lesson_data: UpdateLessonSchema) -> Optional[LessonResponseSchema]:
        """
        Update a lesson.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        lesson = self.db.execute(stmt).scalar_one_or_none()
        
        if not lesson:
            return None
        
        # Update fields
        for field, value in lesson_data.dict(exclude_unset=True).items():
            setattr(lesson, field, value)
        
        self.db.commit()
        self.db.refresh(lesson)
        
        return LessonResponseSchema.model_validate(lesson)
    
    def delete_lesson(self, lesson_id: int) -> bool:
        """
        Delete a lesson.
        """
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        lesson = self.db.execute(stmt).scalar_one_or_none()
        
        if not lesson:
            return False
        
        self.db.delete(lesson)
        self.db.commit()
        
        return True 