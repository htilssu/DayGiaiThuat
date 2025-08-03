from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.exceptions.exception_handler import add_exception_handlers
from app.middleware.camel_case_middleware import CamelCaseMiddleware
from app.routers.router import register_router
from app.socket.socker_chain import add_handler

app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Thêm middleware để chuyển đổi response sang camelCase
app.add_middleware(CamelCaseMiddleware)

# Register routes and exception handlers
register_router(app)
add_handler()
add_exception_handlers(app)
