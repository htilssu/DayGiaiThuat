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
from app.middleware.camel_case_middleware import CamelCaseMiddleware
from app.routers import auth, users, courses

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
    contact={
        "name": "AI Agent Giải Thuật Team",
        "url": "https://github.com/yourusername/your-repo",
        "email": "your-email@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Các API liên quan đến xác thực người dùng",
        },
        {
            "name": "users",
            "description": "Các API liên quan đến quản lý người dùng",
        },
        {
            "name": "courses",
            "description": "Các API liên quan đến quản lý khóa học",
        },
    ],
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)


# Custom Swagger UI với theme và các tùy chỉnh
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
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

# Thêm router
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
