from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.config import settings


def add_exception_handlers(app: FastAPI):
    """
    Thêm các exception handler cho ứng dụng FastAPI.

    :param app: Instance của ứng dụng FastAPI
    """

    # Xử lý lỗi xác thực dữ liệu từ Pydantic
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """
        Xử lý lỗi xác thực dữ liệu từ Pydantic
        """
        if settings.DEV_MODE:
            return JSONResponse(
                status_code=400,
                content={"detail": exc.errors()},
            )
        else:
            return JSONResponse(
                status_code=400, content={"detail": "Invalid request data"}
            )
