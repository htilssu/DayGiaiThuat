from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from typing import Any, Callable
from .base_handler import BaseWebSocketHandler


class ChatConnectionHandler(BaseWebSocketHandler):
    async def handle(self, websocket: WebSocket, message: Any, next: Callable):
        chat_room = message.get("room", "general")
        await self.send_json(
            websocket,
            {
                "type": "chat_ready",
                "room": chat_room,
                "message": f"Ready to chat in room: {chat_room}",
                "features": ["send_message", "receive_messages", "typing_indicators"],
            },
        )

        await broadcast_to_room(
            chat_room,
            {
                "type": "user_joined",
                "room": chat_room,
                "user_id": self.user.id,
                "username": getattr(self.user, "username", "Anonymous"),
                "message": f"{getattr(self.user, 'username', 'Anonymous')} joined the chat",
                "timestamp": datetime.now().isoformat(),
            },
            exclude_connection=self.connection_id,
        )
        while True:
            try:
                data = await self.receive_json()
                message_type = data.get("type", "unknown")
                if message_type == "ping":
                    await self.send_json(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )
                elif message_type == "send_message":
                    message = data.get("message", "")
                    if message.strip():
                        await broadcast_to_room(
                            chat_room,
                            {
                                "type": "chat_message",
                                "room": chat_room,
                                "message": message,
                                "sender_id": self.user.id,
                                "sender_name": getattr(
                                    self.user, "username", "Anonymous"
                                ),
                                "timestamp": datetime.now().isoformat(),
                            },
                            exclude_connection=self.connection_id,
                        )
                        await self.send_json(
                            {
                                "type": "message_sent",
                                "message": message,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                elif message_type == "typing":
                    await broadcast_to_room(
                        chat_room,
                        {
                            "type": "user_typing",
                            "room": chat_room,
                            "user_id": self.user.id,
                            "username": getattr(self.user, "username", "Anonymous"),
                            "timestamp": datetime.now().isoformat(),
                        },
                        exclude_connection=self.connection_id,
                    )
                else:
                    await self.send_json(
                        {
                            "type": "chat_ack",
                            "message": "Message received",
                            "original": data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except WebSocketDisconnect:
                try:
                    await broadcast_to_room(
                        chat_room,
                        {
                            "type": "user_left",
                            "room": chat_room,
                            "user_id": self.user.id,
                            "username": getattr(self.user, "username", "Anonymous"),
                            "message": f"{getattr(self.user, 'username', 'Anonymous')} left the chat",
                            "timestamp": datetime.now().isoformat(),
                        },
                        exclude_connection=self.connection_id,
                    )
                except Exception:
                    pass
                break
            except Exception as e:
                await self.send_json(
                    {"type": "error", "message": f"Chat error: {str(e)}"}
                )
