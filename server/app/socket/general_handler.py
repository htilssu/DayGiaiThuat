from datetime import datetime
from fastapi import WebSocketDisconnect
from .base_handler import BaseWebSocketHandler


class GeneralConnectionHandler(BaseWebSocketHandler):
    async def handle(self):
        await self.send_json(
            {
                "type": "welcome",
                "message": "Welcome to general WebSocket connection",
                "features": ["echo", "broadcast", "room_communication"],
            }
        )
        while True:
            try:
                data = await self.receive_json()
                message_type = data.get("type", "unknown")
                if message_type == "ping":
                    await self.send_json(
                        {"type": "pong", "timestamp": datetime.now().isoformat()}
                    )
                elif message_type == "echo":
                    await self.send_json(
                        {
                            "type": "echo_response",
                            "original_message": data.get("message", ""),
                            "timestamp": datetime.now().isoformat(),
                            "connection_id": self.connection_id,
                        }
                    )
                elif message_type == "join_room":
                    new_room = data.get("room")
                    if new_room:
                        await self.send_json(
                            {
                                "type": "room_joined",
                                "room": new_room,
                                "message": f"Joined room: {new_room}",
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                elif message_type == "broadcast_to_room":
                    target_room = data.get("room", self.room)
                    message = data.get("message", "")
                    if target_room and message:
                        from app.routers.websocket_router import broadcast_to_room

                        await broadcast_to_room(
                            target_room,
                            {
                                "type": "room_message",
                                "room": target_room,
                                "message": message,
                                "sender_id": self.user.id,
                                "sender_name": getattr(
                                    self.user, "username", "Anonymous"
                                ),
                                "timestamp": datetime.now().isoformat(),
                            },
                            exclude_connection=self.connection_id,
                        )
                else:
                    await self.send_json(
                        {
                            "type": "echo",
                            "original_message": data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                await self.send_json(
                    {"type": "error", "message": f"Error processing message: {str(e)}"}
                )
