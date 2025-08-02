from fastapi import FastAPI


def register_router(app: FastAPI):
    """Register all routers with lazy loading for faster startup"""
    from app.routers import (
        admin_courses_router,
        admin_topics_router,
        admin_upload_router,
        ai_chat_router,
        assessment_router,
        auth_router,
        courses_router,
        discussions_router,
        document_router,
        exercise_router,
        lesson_plan_router,
        lesson_router,
        replies_router,
        test_generation_router,
        test_router,
        tutor_router,
        upload_router,
        users_router,
        websocket_router,
    )

    # User routes (không có prefix admin)
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(tutor_router.router)
    app.include_router(exercise_router.router)
    app.include_router(document_router.router)
    app.include_router(document_router.webhook_router)
    app.include_router(test_router.router)
    app.include_router(upload_router.router)
    app.include_router(assessment_router.router)
    app.include_router(lesson_plan_router.router)
    app.include_router(lesson_router.router)
    app.include_router(courses_router.router)
    app.include_router(courses_router.router)

    # WebSocket routes
    app.include_router(websocket_router.router)
    app.include_router(discussions_router.router)
    app.include_router(replies_router.router)
    app.include_router(ai_chat_router.router)

    # Admin routes (có prefix /admin)
    app.include_router(admin_courses_router.router)
    app.include_router(admin_topics_router.router)
    app.include_router(admin_upload_router.router)

    # Test generation routes
    app.include_router(test_generation_router.router)
