# TODO

- [x]: Thêm chức năng thêm topic vào khóa học, ở trong trang chỉnh sửa khóa học, sẽ có 1 trường hoặc nút có thể nhấn vào, khi nhấn vào chuyển sang 1 trang khác chứa danh sách các topic thuộc khóa đó, ở đầu item có check hình tròn, nếu thuộc khóa học đó thì tick = true, nếu không thì không tick, có những chức năng filter, tìm kiếm topic để dễ dàng chỉnh sửa topic cho khóa học

- [x]: Khi mỗi khóa học được tạo, backend sẽ gọi input test agent để tạo ra bài kiểm tra đầu vào, nó sẽ tạo async chứ không đợi tạo xong mới phản hồi về, ở front end sẽ có thêm trạng thái thông tin bài test: 'đang tạo (pending), đã tạo thành công (success), tạo thất bại (fail)', admin cũng có thể yêu cầu tạo thêm nhiều bài test nữa cho khóa học.

- []: Tạo thêm trang để hiển thị thông tin danh sách bài test của khóa học, admin có thể chỉnh sửa nội dung của đề bài
- [x]: Khi người dùng nhấn thông báo làm bài kiểm tra đầu vào, gửi request đến backend tạo session test, sau khi tạo session test thành công, chuyển hướng người dùng đến /test/session_id, fe sẽ dựa vào session_id để truy vấn thông tin bài kiểm tra, khi vào trang đó người dùng sẽ được xác nhận lần nữa, nếu nhấn bắt đầu làm bài kiểm tra thời gian mới được tính
- [x]: bài kiểm tra sẽ sử dụng socket để quản lý lưu đáp án người dùng
