# Sửa lỗi phiên kiểm tra hết hạn (v2 - Không xóa session)

## Vấn đề

Người dùng gặp lỗi khi tạo phiên kiểm tra mới:

```
"Bạn đang có một phiên làm bài kiểm tra khác đang hoạt động. Vui lòng hoàn thành hoặc hủy phiên đó trước khi bắt đầu phiên mới."
```

Mặc dù các phiên trước đã hết hạn thời gian làm bài nhưng vẫn bị coi là đang hoạt động.

## Yêu cầu mới

- **KHÔNG xóa test-session** - giữ lại để người dùng xem lịch sử
- **Chỉ block khi có session thực sự đang trong thời gian làm bài**
- **Session hết hạn/hoàn thành = có thể làm bài mới**

## Giải pháp

### 1. Logic mới cho kiểm tra phiên hoạt động

- **Không thay đổi status** của session hết hạn trong database
- **Chỉ kiểm tra logic** xem session có thực sự active không

#### Phiên `pending`:

- Cho phép tối đa **30 phút** để bắt đầu bài kiểm tra
- Nếu quá 30 phút từ `created_at` → coi như hết hạn

#### Phiên `in_progress`:

- Hết thời gian làm bài (elapsed_time >= `time_remaining_seconds`)
- Không hoạt động quá **30 phút** từ `last_activity`

### 2. Functions mới

#### `has_truly_active_session(user_id)`

- Kiểm tra user có session thực sự đang hoạt động không
- Return `True` nếu có session còn valid, `False` nếu tất cả đã hết hạn

#### `_is_session_truly_active(session, now)`

- Helper method kiểm tra 1 session cụ thể có active không
- Áp dụng logic thời gian cho cả pending và in_progress

#### `count_expired_sessions()`

- Đếm số session hết hạn mà không thay đổi status
- Trả về thông tin chi tiết cho admin

### 3. Endpoint admin mới

- `GET /api/tests/admin/active-sessions-status` - Xem tất cả session đang có status pending/in_progress
- `GET /api/tests/admin/expired-sessions-report` - Báo cáo session hết hạn

## Kiểm tra

### 1. Kiểm tra logic không block

```bash
# 1. Tạo phiên kiểm tra
curl -X POST "http://localhost:8000/api/tests/sessions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "test_id": 1}'

# 2. Đợi 30 phút hoặc thay đổi created_at trong database để simulate hết hạn

# 3. Thử tạo phiên mới - sẽ thành công vì phiên cũ đã hết hạn
curl -X POST "http://localhost:8000/api/tests/sessions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "test_id": 2}'
```

### 2. Kiểm tra endpoint admin

```bash
# Xem tất cả session với status pending/in_progress
curl -X GET "http://localhost:8000/api/tests/admin/active-sessions-status" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Xem báo cáo session hết hạn
curl -X GET "http://localhost:8000/api/tests/admin/expired-sessions-report" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Ưu điểm của giải pháp v2

1. **Bảo toàn dữ liệu**: Không mất lịch sử làm bài của người dùng
2. **Logic chính xác**: Chỉ block khi thực sự cần thiết
3. **Hiệu suất tốt**: Không cần update database mỗi lần kiểm tra
4. **Dễ debug**: Admin có thể xem chi tiết session nào hết hạn và tại sao

## Files đã thay đổi

### `server/app/services/test_service.py`:

- ✅ `create_test_session()` - Sử dụng `has_truly_active_session()`
- ✅ `has_truly_active_session()` - Kiểm tra session thực sự active
- ✅ `_is_session_truly_active()` - Helper method
- ✅ `get_active_session()` - Chỉ trả về session thực sự active
- ✅ `can_access_test_session()` - Không auto-expire
- ✅ `count_expired_sessions()` - Utility cho admin

### `server/app/routers/test_router.py`:

- ✅ `GET /admin/active-sessions-status` - Xem trạng thái session
- ✅ `GET /admin/expired-sessions-report` - Báo cáo session hết hạn

## Test cases đã verify

1. ✅ **Session pending hết hạn**: Có thể tạo session mới
2. ✅ **Session in_progress hết hạn**: Có thể tạo session mới
3. ✅ **Session đang active**: Không thể tạo session mới
4. ✅ **Lịch sử được bảo toàn**: Session cũ vẫn có trong database
