# WebSocket Integration Guide

## Tổng quan

Hệ thống WebSocket được thiết kế để cung cấp kết nối realtime giữa client và server, cho phép nhận thông báo về trạng thái tạo bài học, xử lý tài liệu và các cập nhật khác.

## Cấu trúc

### 1. WebSocketContext (`/contexts/WebSocketContext.tsx`)

Context chính quản lý kết nối WebSocket với các tính năng:

- Kết nối tự động khi ứng dụng khởi động
- Tự động kết nối lại khi mất kết nối
- Xác thực với token
- Quản lý trạng thái kết nối

### 2. WebSocketStatus (`/components/ui/WebSocketStatus.tsx`)

Component hiển thị trạng thái kết nối WebSocket:

- Chấm màu hiển thị trạng thái (xanh: kết nối, đỏ: mất kết nối, vàng: đang kết nối)
- Text mô tả trạng thái (tùy chọn)

### 3. WebSocketNotification (`/components/ui/WebSocketNotification.tsx`)

Component xử lý và hiển thị thông báo từ WebSocket bằng react-hot-toast.

### 4. Hooks (`/hooks/useWebSocket.ts`)

Các hooks tiện ích để sử dụng WebSocket:

- `useWebSocketMessage`: Lắng nghe tin nhắn theo loại
- `useWebSocketSender`: Gửi tin nhắn an toàn
- `useLessonGenerationStatus`: Lắng nghe trạng thái tạo bài học
- `useDocumentProcessingStatus`: Lắng nghe trạng thái xử lý tài liệu
- `useNotification`: Lắng nghe thông báo chung

## Cách sử dụng

### 1. Sử dụng trong Component

```tsx
import { useWebSocket, useLessonGenerationStatus } from "@/hooks";

function MyComponent() {
  const { isConnected, sendMessage } = useWebSocket();

  // Lắng nghe trạng thái tạo bài học
  useLessonGenerationStatus((status) => {
    console.log("Lesson generation status:", status);
  });

  const handleSendMessage = () => {
    sendMessage({
      type: "custom_message",
      data: { content: "Hello server!" },
    });
  };

  return (
    <div>
      <p>Kết nối: {isConnected ? "Đã kết nối" : "Chưa kết nối"}</p>
      <button onClick={handleSendMessage}>Gửi tin nhắn</button>
    </div>
  );
}
```

### 2. Hiển thị trạng thái kết nối

```tsx
import WebSocketStatus from "@/components/ui/WebSocketStatus";

function Header() {
  return (
    <div>
      <WebSocketStatus showText={true} />
    </div>
  );
}
```

### 3. Lắng nghe tin nhắn tùy chỉnh

```tsx
import { useWebSocketMessage } from "@/hooks";

function CustomComponent() {
  useWebSocketMessage("custom_event", (data) => {
    console.log("Received custom event:", data);
  });

  return <div>Listening for custom events...</div>;
}
```

## Các loại tin nhắn WebSocket

### 1. Trạng thái tạo bài học

```json
{
  "type": "lesson_generation_status",
  "data": {
    "status": "started|processing|completed|error",
    "progress": 50,
    "message": "Đang tạo bài học...",
    "topic_id": "123"
  }
}
```

### 2. Trạng thái xử lý tài liệu

```json
{
  "type": "document_processing_status",
  "data": {
    "status": "started|processing|completed|error",
    "progress": 75,
    "message": "Đang xử lý tài liệu...",
    "filename": "document.pdf"
  }
}
```

### 3. Thông báo chung

```json
{
  "type": "notification",
  "data": {
    "title": "Thông báo",
    "message": "Có cập nhật mới",
    "type": "info|success|warning|error",
    "duration": 5000
  }
}
```

### 4. Lỗi

```json
{
  "type": "error",
  "data": {
    "message": "Có lỗi xảy ra",
    "code": "ERROR_CODE"
  }
}
```

## Cấu hình

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### WebSocket URL

URL WebSocket được tự động tạo dựa trên `NEXT_PUBLIC_API_URL`:

- HTTP → WS: `ws://localhost:8000/ws`
- HTTPS → WSS: `wss://your-domain.com/ws`

## Xử lý lỗi

1. **Kết nối thất bại**: Tự động thử kết nối lại với exponential backoff
2. **Mất kết nối**: Tự động kết nối lại tối đa 5 lần
3. **Tin nhắn không hợp lệ**: Log lỗi và bỏ qua
4. **Lỗi xác thực**: Thông báo lỗi cho người dùng

## Best Practices

1. **Chỉ lắng nghe tin nhắn cần thiết**: Sử dụng hooks chuyên biệt thay vì lắng nghe tất cả
2. **Cleanup listeners**: Hooks tự động cleanup khi component unmount
3. **Kiểm tra kết nối**: Luôn kiểm tra `isConnected` trước khi gửi tin nhắn
4. **Xử lý loading states**: Hiển thị loading trong khi chờ phản hồi từ server

## Troubleshooting

### WebSocket không kết nối được

1. Kiểm tra `NEXT_PUBLIC_API_URL` trong `.env.local`
2. Đảm bảo server WebSocket đang chạy
3. Kiểm tra network/firewall settings

### Không nhận được thông báo

1. Kiểm tra console để xem có lỗi không
2. Đảm bảo component đã được wrap trong `WebSocketProvider`
3. Kiểm tra server có gửi đúng format không

### Kết nối bị đứt liên tục

1. Kiểm tra server stability
2. Đảm bảo không có multiple connections từ cùng một user
3. Kiểm tra network quality
