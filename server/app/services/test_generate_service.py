
async def run_course_composition_background(
        request: CourseCompositionRequestSchema, db: AsyncSession
):
    """
    Hàm chạy trong background để tạo nội dung khóa học.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        agent = CourseCompositionAgent(db)
        agent_response, session_id = await agent.act(request)

        import json
        from sqlalchemy import select
        from datetime import datetime

        # Tìm draft hiện tại của course này
        existing_draft_result = await db.execute(
            select(CourseDraft).filter(CourseDraft.course_id == request.course_id)
        )
        existing_draft = existing_draft_result.scalar_one_or_none()

        topics_json = json.dumps(
            agent_response.model_dump(), ensure_ascii=False, indent=2
        )

        if existing_draft:
            # Cập nhật draft hiện có
            existing_draft.agent_content = topics_json
            existing_draft.session_id = session_id
            existing_draft.status = "pending"
            existing_draft.updated_at = datetime.utcnow()
        else:
            # Tạo draft mới nếu chưa có
            new_draft = CourseDraft(
                course_id=request.course_id,
                agent_content=topics_json,
                session_id=session_id,
                status="pending",
            )
            db.add(new_draft)

        await db.commit()
        logger.info(
            f"✅ Course composition completed and saved to draft for course: {request.course_id} with session: {session_id}"
        )

    except Exception as e:
        logger.error(f"❌ Error in course composition: {str(e)}")
        await db.rollback()
        raise e