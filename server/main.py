import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html

from app.core.config import settings
from app.exceptions.exception_handler import add_exception_handlers
from app.routers.router import register_router
from app.middleware.camel_case_middleware import CamelCaseMiddleware


# Khởi tạo logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## API Documentation
    ## Tài liệu API

    * **/docs** - Swagger UI (hiện tại)
    * **/redoc** - ReDoc UI
    """,
    version="1.0.0",
    openapi_url="/openapi.json",
    contact={
        "name": "AI Agent Giải Thuật Team",
        "url": "https://github.com/yourusername/your-repo",
        "email": "your-email@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - ReDoc",
    )


# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm middleware để chuyển đổi response sang camelCase
app.add_middleware(CamelCaseMiddleware)

register_router(app)

add_exception_handlers(app)
