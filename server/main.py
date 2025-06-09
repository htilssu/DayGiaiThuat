import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from app.core.config import settings
from app.database.database import run_migrations
from app.database.seeder import run_seeder_async
from app.exceptions.exception_handler import add_exception_handlers
from app.middleware.camel_case_middleware import CamelCaseMiddleware
from app.routers.router import register_router

# Khởi tạo logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager để quản lý vòng đời của ứng dụng.
    Mã trong phần 'yield' trước sẽ chạy khi khởi động,
    và mã sau 'yield' sẽ chạy khi kết thúc.

    Args:
        app (FastAPI): Instance của ứng dụng FastAPI
    """
    # Startup: chạy khi ứng dụng khởi động
    logger.info("Ứng dụng đang khởi động...")

    # Chạy migration nếu được cấu hình
    if getattr(settings, "RUN_MIGRATIONS_ON_STARTUP", False):
        logger.info("Chạy migrations tự động...")
        run_migrations()

    # Chạy seeder nếu được cấu hình
    if getattr(settings, "RUN_SEEDERS_ON_STARTUP", False):
        logger.info("Chạy seeders tự động...")
        seeders_to_run = getattr(settings, "SEEDERS_TO_RUN", None)
        force_seeders = getattr(settings, "FORCE_SEEDERS", False)
        try:
            await run_seeder_async(seeders=seeders_to_run, force=force_seeders)
        except Exception as e:
            logger.error(f"Lỗi khi chạy seeders: {str(e)}")

    yield

    # Shutdown: chạy khi ứng dụng kết thúc
    logger.info("Đóng kết nối và dọn dẹp tài nguyên...")


# Khởi tạo FastAPI app với lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""

    ## Tài liệu API

    * **/docs** - Swagger UI (hiện tại)
    * **/redoc** - ReDoc UI
    """,
    version="1.0.0",
    openapi_url=f"/openapi.json",
    contact={
        "name": "AI Agent Giải Thuật Team",
        "url": "https://github.com/yourusername/your-repo",
        "email": "your-email@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)


# Custom Swagger UI với theme và các tùy chỉnh
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Swagger UI",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - ReDoc",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


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
