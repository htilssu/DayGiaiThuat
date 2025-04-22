"""
Middleware để chuyển đổi FastAPI request sang snake_case và response sang camelCase
"""
from http.client import responses
from typing import Callable, Optional

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Scope, Receive, Send
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
        self.initial_message = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Xử lý request body từ camelCase sang snake_case
        request = Request(scope, receive)
        request = await self._process_request(request)


        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                self.initial_message = message
            elif message["type"] == "http.response.body":
                # Chỉ xử lý response có body là JSON
                is_json = False
                content_type = None
                for key, value in self.initial_message["headers"]:
                    if key == b"content-type" and b"application/json" in value:
                        is_json = True
                        content_type = value
                        break

                if is_json and message.get("body"):
                    try:
                        # Chuyển đổi từ snake_case sang camelCase
                        original_body = message["body"]
                        body_dict = json.loads(original_body)
                        camel_case_dict = convert_dict_to_camel_case(body_dict)
                        new_body = json.dumps(camel_case_dict).encode()
                        message["body"] = new_body

                        # Cập nhật Content-Length trong header
                        headers = MutableHeaders(raw=self.initial_message["headers"])

                        headers["content-length"] = str(len(new_body))

                        await send(self.initial_message)
                        await send(message)

                        return
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Nếu không phải JSON hợp lệ thì gửi nguyên body
                        pass

        await self.app(scope, request._receive, send_wrapper)

    async def _process_request(self, request: Request) -> Request:
        """
        Chuyển đổi request body từ camelCase (frontend) sang snake_case (backend)
        """
        # Kiểm tra request có body JSON không
        if request.headers.get("content-type") == "application/json":
            request_body = await request.body()
            if request_body:
                # Đọc và chuyển đổi body từ camelCase sang snake_case
                try:
                    body_dict = json.loads(request_body)
                    snake_case_body = convert_dict_to_snake_case(body_dict)

                    # Ghi đè body của request
                    async def receive():
                        return {
                            "type": "http.request",
                            "body": json.dumps(snake_case_body).encode(),
                        }

                    request._receive = receive
                except json.JSONDecodeError:
                    # Nếu body không phải JSON hợp lệ thì giữ nguyên
                    pass

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
