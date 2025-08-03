import { MarkdownRenderer } from './MarkdownRenderer';

const sampleMarkdownWithTable = `
# Demo Table Rendering

Đây là ví dụ về việc hiển thị bảng trong markdown:

## Bảng cơ bản

| Tên | Tuổi | Nghề nghiệp | Mức lương |
|-----|------|-------------|-----------|
| Nguyễn Văn A | 25 | Lập trình viên | 15,000,000 VNĐ |
| Trần Thị B | 30 | Designer | 12,000,000 VNĐ |
| Lê Văn C | 28 | Product Manager | 20,000,000 VNĐ |
| Phạm Thị D | 26 | QA Tester | 10,000,000 VNĐ |

## Bảng với căn lề

| Left-aligned | Center-aligned | Right-aligned |
|:-------------|:--------------:|--------------:|
| Căn trái     | Căn giữa       | Căn phải      |
| Dữ liệu 1    | Dữ liệu 2      | Dữ liệu 3     |
| Text dài hơn | Nội dung       | 999,999       |

## Bảng thông tin khóa học

| Khóa học | Thời lượng | Độ khó | Giá | Đánh giá |
|----------|------------|--------|-----|----------|
| **React Fundamentals** | 40 giờ | ⭐⭐⭐ | Miễn phí | 4.8/5 |
| **Advanced JavaScript** | 60 giờ | ⭐⭐⭐⭐⭐ | 1,500,000 VNĐ | 4.9/5 |
| **Node.js Backend** | 50 giờ | ⭐⭐⭐⭐ | 2,000,000 VNĐ | 4.7/5 |
| **Database Design** | 35 giờ | ⭐⭐⭐ | 1,200,000 VNĐ | 4.6/5 |

## Features được hỗ trợ:

- ✅ **Responsive design**: Table tự động scroll khi màn hình nhỏ
- ✅ **Hover effects**: Highlight row khi hover
- ✅ **Professional styling**: Thiết kế chuyên nghiệp với shadow và border
- ✅ **Typography**: Font size và spacing được tối ưu
- ✅ **Alignment support**: Hỗ trợ căn trái, giữa, phải
- ✅ **GitHub Flavored Markdown**: Sử dụng remark-gfm cho syntax chuẩn

> **Lưu ý:** Table markdown sẽ tự động được render với styling đẹp mắt và responsive.
`;

export function TableDemo() {
    return (
        <div className="max-w-4xl mx-auto p-6">
            <MarkdownRenderer content={sampleMarkdownWithTable} />
        </div>
    );
}
