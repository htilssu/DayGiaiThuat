from datetime import datetime
from fastapi import WebSocketDisconnect
from .base_handler import BaseWebSocketHandler


class TestSessionConnectionHandler(BaseWebSocketHandler):
    async def handle(self):
        session_id = self.room
        if not session_id:
            await self.send_json(
                {
                    "type": "error",
                    "message": "session_id (room parameter) is required for test-session connection",
                }
            )
            return
        await self.send_json(
            {
                "type": "test_session_ready",
                "session_id": session_id,
                "message": "Ready to monitor test session",
                "features": ["timer_updates", "answer_sync", "auto_submit"],
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
                elif message_type == "get_session_status":
                    await self.send_json(
                        {
                            "type": "session_status",
                            "session_id": session_id,
                            "status": "active",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                elif message_type == "heartbeat":
                    await self.send_json(
                        {
                            "type": "heartbeat_ack",
                            "session_id": session_id,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    await self.send_json(
                        {
                            "type": "test_session_ack",
                            "message": "Message received",
                            "session_id": session_id,
                            "original": data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                await self.send_json(
                    {"type": "error", "message": f"Test session error: {str(e)}"}
                )
