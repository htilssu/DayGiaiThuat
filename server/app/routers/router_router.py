from fastapi import FastAPI

from app.routers import (
    auth_router,
    courses_router,
    document_router,
    exercise_router,
    tutor_router,
    users_router,
)


def register_router(app: FastAPI):
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(courses_router.router)
    app.include_router(tutor_router.router)
    app.include_router(exercise_router.router)
    app.include_router(document_router.router)
