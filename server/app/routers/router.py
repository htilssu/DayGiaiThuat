from fastapi import FastAPI

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
)


def register_router(app: FastAPI):
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

    # Admin routes (có prefix /admin)
    app.include_router(admin_courses_router.router)
    app.include_router(admin_topics_router.router)
    app.include_router(admin_upload_router.router)
