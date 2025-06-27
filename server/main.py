import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html

from app.core.config import settings
from app.exceptions.exception_handler import add_exception_handlers
from app.routers.router import register_router
from app.middleware.camel_case_middleware import CamelCaseMiddleware


# Khởi tạo logger
logger = logging.getLogger(__name__)


async def monitor_test_sessions():
    """Background task để theo dõi và xử lý session timeout"""
    from app.services.test_service import get_test_service
    from app.database.database import get_async_session

    while True:
        try:
            # Check every 30 seconds
            await asyncio.sleep(30)

            # Get database session
            async for session in get_async_session():
                test_service = get_test_service(session)
                await test_service.check_and_update_expired_sessions()
                break

        except Exception as e:
            print(f"Error in monitor_test_sessions: {e}")
            await asyncio.sleep(60)  # Wait longer on error


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")

    # Start background task for monitoring test sessions
    monitor_task = asyncio.create_task(monitor_test_sessions())

    yield

    # Shutdown
    print("Shutting down...")
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


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
    lifespan=lifespan,
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

# Register routes and exception handlers
register_router(app)
add_exception_handlers(app)
