from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


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
        return JSONResponse(
            status_code=400,
            content={
                "detail": [
                    {
                        "field": error["loc"][1],
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ]
            },
        )
