from fastapi import FastAPI

from app.routers import auth, users, courses, tutor, exercise, document


def register_router(app: FastAPI):
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(courses.router)
    app.include_router(tutor.router)
    app.include_router(exercise.router)
    app.include_router(document.router)
