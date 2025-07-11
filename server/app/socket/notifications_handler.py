from datetime import datetime
from fastapi import WebSocketDisconnect
from .base_handler import BaseWebSocketHandler


class NotificationsConnectionHandler(BaseWebSocketHandler):
    async def handle(self):
        await self.send_json(
            {
                "type": "notifications_ready",
                "message": "Ready to receive notifications",
                "features": [
                    "system_notifications",
                    "user_notifications",
                    "real_time_updates",
                ],
            }
        )
        await self.send_json(
            {
                "type": "notification",
                "title": "Welcome!",
                "message": "You are now connected to receive real-time notifications",
                "priority": "info",
                "timestamp": datetime.now().isoformat(),
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
                elif message_type == "mark_notification_read":
                    notification_id = data.get("notification_id")
                    await self.send_json(
                        {
                            "type": "notification_marked_read",
                            "notification_id": notification_id,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    await self.send_json(
                        {
                            "type": "notification_ack",
                            "message": "Message received",
                            "original": data,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                await self.send_json(
                    {"type": "error", "message": f"Notification error: {str(e)}"}
                )
