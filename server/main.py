from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.exc
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

from app.database.database import engine, Base
from app.routers import auth
from app.core.config import settings

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    🚀 API hệ thống xác thực với FastAPI

    ## Tính năng

    * **Đăng ký** - Tạo tài khoản mới
    * **Đăng nhập** - Xác thực và lấy token
    * **Quản lý profile** - Xem và cập nhật thông tin cá nhân

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
    ],
    docs_url=None,
    redoc_url=None,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# Thêm router
app.include_router(auth.router, prefix=settings.API_V1_STR)

# Tạo database tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database connected successfully!")
except sqlalchemy.exc.OperationalError as e:
    print(f"Could not connect to database: {e}")
    # Không raise exception ở đây để ứng dụng vẫn khởi động được
    # ngay cả khi không kết nối được database

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint
    
    Returns:
        dict: Thông tin welcome
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/hello/{name}", tags=["examples"])
async def say_hello(name: str):
    """
    Chào một người dùng
    
    Args:
        name (str): Tên người dùng
        
    Returns:
        dict: Lời chào
    """
    return {"message": f"Hello {name}"}
