"""
Middleware để chuyển đổi FastAPI request sang snake_case và response sang camelCase
"""
from http.client import responses
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json
from app.utils.case_utils import convert_dict_to_camel_case, convert_dict_to_snake_case


class CamelCaseMiddleware:
    """
    Middleware tự động chuyển đổi:
    - Request từ camelCase sang snake_case để phù hợp với backend Python
    - Response từ snake_case sang camelCase để phù hợp với frontend
    """

    def __init__(
            self,
            app,
    ) -> None:
        self.app = app

    async def __call__(
            self, scope, receive, send
    ):
        # Xử lý request body từ camelCase sang snake_case
        request = Request(scope, receive)
        request = await    self._process_request(request)

        await self.app(scope, request._receive, send)

    async def _process_request(self, request: Request) -> Request:
        """
        Chuyển đổi request body từ camelCase (frontend) sang snake_case (backend)
        """
        # Kiểm tra request có body JSON không
        if request.headers.get("content-type") == "application/json":
            request_body = await request.body()
            if request_body:
                # Đọc và chuyển đổi body từ camelCase sang snake_case
                body_dict = json.loads(request_body)
                snake_case_body = convert_dict_to_snake_case(body_dict)

                # Ghi đè body của request
                async def receive():
                    return {
                        "type": "http.request",
                        "body": json.dumps(snake_case_body).encode(),
                    }

                request._receive = receive

        return request

    async def _process_response(self, response: Response) -> Response:
        """
        Chuyển đổi response body từ snake_case (backend) sang camelCase (frontend)
        """
        # Chỉ xử lý JSON responses
        if isinstance(response, JSONResponse):
            response_body = json.loads(response.body)
            # Chuyển đổi tất cả key trong response sang camelCase
            camel_case_body = convert_dict_to_camel_case(response_body)
            # Tạo response mới với body đã được chuyển đổi
            return JSONResponse(
                status_code=response.status_code,
                content=camel_case_body,
                headers=dict(response.headers),
                media_type=response.media_type,
                background=response.background,
            )

        return response
