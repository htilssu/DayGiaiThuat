# WebSocket Router Tổng Quát - /ws

## Tổng quan

Đây là WebSocket endpoint tổng quát tại `localhost:8000/ws` có thể xử lý nhiều loại kết nối real-time khác nhau.

## Endpoint

```
WS localhost:8000/ws
```

## Authentication

Tất cả kết nối WebSocket đều yêu cầu authentication qua JWT token trong query parameters:

```
ws://localhost:8000/ws?token=YOUR_JWT_TOKEN&connection_type=general
```

## Các Loại Kết Nối (Connection Types)

### 1. General Connection (`general`)

Kết nối chung cho giao tiếp real-time và thử nghiệm.

**URL:**
```
ws://localhost:8000/ws?connection_type=general&token=YOUR_TOKEN
```

**Features:**
- Echo messages
- Ping/Pong heartbeat
- Room communication
- Broadcast messages

**Example Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?connection_type=general&token=your_token');

ws.onopen = function() {
    // Send ping
    ws.send(JSON.stringify({
        type: 'ping'
    }));
    
    // Send echo message
    ws.send(JSON.stringify({
        type: 'echo',
        message: 'Hello WebSocket!'
    }));
    
    // Join room
    ws.send(JSON.stringify({
        type: 'join_room',
        room: 'room1'
    }));
    
    // Broadcast to room
    ws.send(JSON.stringify({
        type: 'broadcast_to_room',
        room: 'room1',
        message: 'Hello everyone in room1!'
    }));
};
```

### 2. Notifications Connection (`notifications`)

Nhận thông báo real-time từ hệ thống.

**URL:**
```
ws://localhost:8000/ws?connection_type=notifications&token=YOUR_TOKEN
```

**Features:**
- System notifications
- User-specific notifications
- Read receipt tracking

**Example Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?connection_type=notifications&token=your_token');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'notification') {
        // Display notification
        showNotification(data.title, data.message, data.priority);
        
        // Mark as read
        ws.send(JSON.stringify({
            type: 'mark_notification_read',
            notification_id: data.id
        }));
    }
};
```

### 3. Test Session Connection (`test-session`)

Giám sát phiên làm bài kiểm tra real-time.

**URL:**
```
ws://localhost:8000/ws?connection_type=test-session&room=SESSION_ID&token=YOUR_TOKEN
```

**Features:**
- Session status monitoring
- Timer updates
- Answer synchronization
- Auto-submit handling

**Example Usage:**
```javascript
const sessionId = 'your-session-id';
const ws = new WebSocket(`ws://localhost:8000/ws?connection_type=test-session&room=${sessionId}&token=your_token`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'test_session_ready':
            console.log('Test session monitoring ready');
            break;
            
        case 'session_status':
            updateSessionUI(data);
            break;
    }
};

// Get session status
ws.send(JSON.stringify({
    type: 'get_session_status'
}));
```

### 4. Chat Connection (`chat`)

Chat real-time trong các phòng chat.

**URL:**
```
ws://localhost:8000/ws?connection_type=chat&room=ROOM_NAME&token=YOUR_TOKEN
```

**Features:**
- Send/receive messages
- User join/leave notifications
- Typing indicators
- Multiple chat rooms

**Example Usage:**
```javascript
const chatRoom = 'general';
const ws = new WebSocket(`ws://localhost:8000/ws?connection_type=chat&room=${chatRoom}&token=your_token`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'chat_message':
            displayMessage(data.sender_name, data.message, data.timestamp);
            break;
            
        case 'user_joined':
            showUserJoined(data.username);
            break;
            
        case 'user_left':
            showUserLeft(data.username);
            break;
            
        case 'user_typing':
            showTypingIndicator(data.username);
            break;
    }
};

// Send message
function sendMessage(message) {
    ws.send(JSON.stringify({
        type: 'send_message',
        message: message
    }));
}

// Send typing indicator
function sendTyping() {
    ws.send(JSON.stringify({
        type: 'typing'
    }));
}
```

## Management API (Admin Only)

### 1. Get WebSocket Statistics

```http
GET /ws/stats
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Response:**
```json
{
    "total_connections": 15,
    "total_users": 8,
    "connections_by_type": {
        "general": 5,
        "notifications": 4,
        "test-session": 3,
        "chat": 3
    },
    "connections_by_user": {
        "1": 2,
        "2": 3,
        "3": 1
    }
}
```

### 2. Broadcast Message

```http
POST /ws/broadcast
Authorization: Bearer YOUR_ADMIN_TOKEN
Content-Type: application/json

{
    "type": "system_announcement",
    "title": "Maintenance Notice",
    "message": "System will be down for maintenance in 30 minutes",
    "priority": "high"
}
```

**Optional Query Parameters:**
- `connection_type`: Broadcast to specific connection type only
- `user_id`: Broadcast to specific user only
- `room`: Broadcast to specific room only

### 3. Disconnect Connection

```http
DELETE /ws/connections/{connection_id}
Authorization: Bearer YOUR_ADMIN_TOKEN
```

## Message Format

Tất cả messages đều theo format JSON:

```json
{
    "type": "message_type",
    "data": "message_data",
    "timestamp": "2025-07-10T10:30:00.000Z"
}
```

## Error Handling

WebSocket sẽ gửi error messages với format:

```json
{
    "type": "error",
    "message": "Error description",
    "timestamp": "2025-07-10T10:30:00.000Z"
}
```

## Connection Management

- Mỗi connection có unique ID: `{type}_{user_id}_{timestamp}`
- Automatic cleanup khi disconnect
- Broken connections được phát hiện và loại bỏ tự động
- User có thể có nhiều connections cùng lúc

## Security Features

- JWT token authentication required
- User-specific access control
- Admin-only management endpoints
- Automatic connection tracking và cleanup

## Testing với JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <div id="messages"></div>
    <input id="messageInput" type="text" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>
    <button onclick="sendPing()">Ping</button>

    <script>
        const token = 'your_jwt_token_here';
        const ws = new WebSocket(`ws://localhost:8000/ws?connection_type=general&token=${token}`);
        
        ws.onopen = function() {
            addMessage('Connected to WebSocket');
        };
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            addMessage(`Received: ${JSON.stringify(data, null, 2)}`);
        };
        
        ws.onclose = function(event) {
            addMessage(`Disconnected: ${event.code} - ${event.reason}`);
        };
        
        ws.onerror = function(error) {
            addMessage(`Error: ${error}`);
        };
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value;
            if (message) {
                ws.send(JSON.stringify({
                    type: 'echo',
                    message: message
                }));
                input.value = '';
            }
        }
        
        function sendPing() {
            ws.send(JSON.stringify({
                type: 'ping'
            }));
        }
        
        function addMessage(message) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

Lưu code trên vào file HTML và mở trong browser để test WebSocket connection!
