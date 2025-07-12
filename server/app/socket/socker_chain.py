from app.socket.base_handler import BaseWebSocketHandler
from fastapi import WebSocket
from typing import Any

chain_handler: list[BaseWebSocketHandler] = []


def add_handler():
    from app.socket.learn_handler import LearnConnectionHandler

    chain_handler.append(LearnConnectionHandler())


def remove_handler(handler: BaseWebSocketHandler):
    chain_handler.remove(handler)


async def process_message(websocket: WebSocket, message: Any):
    current_handler = chain_handler[0]
    current_handler_index = 0
    length = len(chain_handler)

    async def next():
        nonlocal current_handler_index
        nonlocal current_handler
        if current_handler_index < length - 1:
            current_handler_index += 1
            current_handler = chain_handler[current_handler_index]
            await current_handler.handle(websocket, message, next)
        else:
            await current_handler.handle(websocket, message, lambda: print("end"))

    await current_handler.handle(websocket, message, next)
