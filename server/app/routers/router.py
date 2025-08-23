from fastapi import FastAPI

from app.routers.document_router import webhook_router


def register_router(app: FastAPI):
    """Register all routers with lazy loading for faster startup"""
    from app.routers import (
        admin_courses_router,
        admin_topics_router,
        admin_upload_router,
        auth_router,
        courses_router,
        discussions_router,
        document_router,
        exercise_router,
        exercise_test_case_router,
        lesson_plan_router,
        lesson_router,
        replies_router,
        test_generation_router,
        test_router,
        tutor_router,
        upload_router,
        user_assessment_router,
        ai_chat_router,
        users_router,
        websocket_router,
    )

    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(tutor_router.router)
    app.include_router(document_router.router)
    app.include_router(exercise_router.router)
    app.include_router(ai_chat_router.router)
    app.include_router(test_router.router)
    app.include_router(upload_router.router)
    app.include_router(lesson_plan_router.router)
    app.include_router(lesson_router.router)
    app.include_router(webhook_router)
    app.include_router(courses_router.router)
    app.include_router(websocket_router.router)
    app.include_router(discussions_router.router)
    app.include_router(replies_router.router)
    app.include_router(admin_courses_router.router)
    app.include_router(admin_topics_router.router)
    app.include_router(admin_upload_router.router)
    app.include_router(test_generation_router.router)
    app.include_router(user_assessment_router.router)
    app.include_router(exercise_test_case_router.router)
