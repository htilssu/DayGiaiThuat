from fastapi import FastAPI


def register_router(app: FastAPI):
    """Register all routers with lazy loading for faster startup"""

    # Lazy import để tăng tốc startup
    from app.routers import (
        auth_router,
        courses_router,
        document_router,
        exercise_router,
        test_router,
        tutor_router,
        topic_router,
        users_router,
        upload_router,
        admin_courses_router,
        admin_topics_router,
        admin_upload_router,
        test_generation_router,
        assessment_router,
        discussions_router,
        replies_router,
        ai_chat_router,
    )

    # User routes (không có prefix admin)
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(courses_router.router)
    app.include_router(tutor_router.router)
    app.include_router(exercise_router.router)
    app.include_router(document_router.router)
    app.include_router(test_router.router)
    app.include_router(topic_router.router)
    app.include_router(upload_router.router)
    app.include_router(assessment_router.router)
    app.include_router(discussions_router.router)
    app.include_router(replies_router.router)
    app.include_router(ai_chat_router.router)

    # Admin routes (có prefix /admin)
    app.include_router(admin_courses_router.router)
    app.include_router(admin_topics_router.router)
    app.include_router(admin_upload_router.router)

    # Test generation routes
    app.include_router(test_generation_router.router)
