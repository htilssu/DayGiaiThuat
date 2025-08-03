import json
from fastapi import Request
from starlette.datastructures import MutableHeaders
from starlette.types import Message, Scope, Receive, Send

from app.utils.case_utils import convert_dict_to_camel_case, convert_dict_to_snake_case


async def _process_request(request: Request) -> Request:
    if request.headers.get("content-type") == "application/json":
        body_bytes = await request.body()
        if body_bytes:
            try:
                body_dict = json.loads(body_bytes)
                snake_case_body = convert_dict_to_snake_case(body_dict)

                # Store the original receive function
                original_receive = request._receive
                body_sent = False

                async def receive():
                    nonlocal body_sent

                    # If body hasn't been sent yet, send the processed body
                    if not body_sent:
                        body_sent = True
                        return {
                            "type": "http.request",
                            "body": json.dumps(snake_case_body).encode(),
                            "more_body": False,
                        }

                    message = await original_receive()
                    return message

                request._receive = receive

            except json.JSONDecodeError:
                pass
    return request


class CamelCaseMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            await self.app(scope, receive, send)
            return

        if scope["type"] == "websocket":
            await self._handle_websocket(scope, receive, send)
            return

        request = Request(scope, receive)
        request = await _process_request(request)

        initial_message = {}

        async def send_wrapper(message: Message):
            nonlocal initial_message

            if message["type"] == "http.response.start":
                initial_message = message
                return

            if message["type"] == "http.response.body":
                # Đảm bảo header đã gửi
                if initial_message:
                    content_type = ""
                    for key, value in initial_message["headers"]:
                        if key == b"content-type":
                            content_type = value.decode()
                            break

                    is_streaming = any(
                        stream_type in content_type
                        for stream_type in [
                            "text/event-stream",
                            "text/plain",
                            "application/octet-stream",
                            "text/stream",
                        ]
                    )

                    if is_streaming:
                        await send(initial_message)
                        initial_message = None
                        await send(message)
                        return

                    # Nếu là JSON response thì chuyển snake_case -> camelCase
                    if "application/json" in content_type and message.get("body"):
                        try:
                            body_dict = json.loads(message["body"])
                            camel_case_body = convert_dict_to_camel_case(body_dict)
                            new_body = json.dumps(camel_case_body).encode()
                            message["body"] = new_body

                            headers = MutableHeaders(raw=initial_message["headers"])
                            del headers["content-length"]

                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass  # Không phải JSON hợp lệ thì bỏ qua

                    await send(initial_message)
                    initial_message = None

            await send(message)

        await self.app(scope, request._receive, send_wrapper)

    async def _handle_websocket(self, scope: Scope, receive: Receive, send: Send):
        async def receive_wrapper():
            message = await receive()
            if message["type"] == "websocket.receive" and "text" in message:
                try:
                    data = json.loads(message["text"])
                    snake_case_data = convert_dict_to_snake_case(data)
                    message["text"] = json.dumps(snake_case_data)
                except (json.JSONDecodeError, TypeError):
                    pass
            return message

        async def send_wrapper(message: Message):
            if message["type"] == "websocket.send" and "text" in message:
                try:
                    data = json.loads(message["text"])
                    camel_case_data = convert_dict_to_camel_case(data)
                    message["text"] = json.dumps(camel_case_data)
                except (json.JSONDecodeError, TypeError):
                    pass
            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)
