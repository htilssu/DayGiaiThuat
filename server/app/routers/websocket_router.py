from bidict import bidict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import settings
from app.socket.socker_chain import process_message
from app.utils.utils import ALGORITHM

router = APIRouter()
active_connections: bidict[str, WebSocket] = bidict()


def get_current_user_ws(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    user_id = token
    # Đảm bảo mỗi user chỉ có 1 kết nối
    if user_id in active_connections:
        try:
            await active_connections[user_id].close(
                code=status.WS_1000_NORMAL_CLOSURE,
                reason="New connection from same user",
            )
        except Exception:
            pass
    active_connections[user_id] = websocket
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await process_message(websocket, data)
    except WebSocketDisconnect:
        pass
    finally:
        if user_id in active_connections and active_connections[user_id] == websocket:
            print(f"User {user_id} disconnected")
            del active_connections[user_id]
