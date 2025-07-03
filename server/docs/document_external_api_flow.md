# Document External API Processing Flow

## Tổng quan

Flow xử lý document đã được thay đổi để sử dụng external API thay vì xử lý trực tiếp trên server. Quy trình mới như sau:

1. **Admin upload document** → Upload lên object storage
2. **Gọi external API** với URL của document
3. **Nhận kết quả** từ external API

## Kiến trúc mới

```
Admin → Upload File → Object Storage → External API Call → Process Complete
                   ↓                       ↓
                [Document URL]        [API Response]
```

## Cấu hình

### Environment Variables

Thêm vào file `.env`:

```bash
# Document Processing Settings
DOCUMENT_PROCESSING_ENDPOINT=https://your-api-endpoint.com/process
DOCUMENT_PROCESSING_TIMEOUT=300
S3_DOCUMENT_PREFIX=documents/
```

### Object Storage

Document sẽ được upload lên object storage (S3/Cloudflare R2) với:

- **Prefix**: `documents/`
- **Format**: `documents/yyyy-mm-dd/uuid.ext`
- **Max Size**: 100MB
- **Supported Types**: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG, TIFF, BMP, GIF

## API Endpoints

### Upload Document

**POST** `/admin/document/store`

**Headers:**

```
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data
```

**Body:**

```
files: [File1, File2, ...]
```

**Response:**

```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "status": "processing",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

### Check Status

**GET** `/admin/document/status?ids=uuid1,uuid2`

**Response:**

```json
[
  {
    "id": "uuid",
    "filename": "document.pdf",
    "status": "completed",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "external_response": {
      // Response từ external API
    }
  }
]
```

## External API Interface

### Request Format

API endpoint sẽ nhận request với format:

```json
{
  "input": {
    "url": "https://storage.example.com/documents/2024-01-01/uuid.pdf"
  }
}
```

### Headers

```
Content-Type: application/json
```

### Response

External API có thể trả về bất kỳ JSON format nào. Response sẽ được lưu trong `external_response` field.

## Xử lý lỗi

### Timeout

- **Timeout**: 300 seconds (configurable)
- **Error**: Status = "failed", error message ghi timeout

### HTTP Errors

- **4xx/5xx**: Status = "failed", error message ghi HTTP status và response

### Network Errors

- **Connection failed**: Status = "failed", error message ghi lỗi network

## Security

### Admin Access

- Chỉ admin mới có thể upload documents
- Kiểm tra quyền thông qua JWT token

### File Validation

- Kiểm tra file type
- Giới hạn kích thước (100MB)
- Sanitize filename

### Object Storage

- Documents không được set public ACL
- URL có thể sử dụng signed URL nếu cần

## Monitoring

### Status Tracking

- `processing`: Đang gọi external API
- `completed`: API response thành công
- `failed`: Có lỗi xảy ra

### Logging

- Upload events
- API calls và responses
- Error details

## Migration

### Từ DocLing/Document AI

Nếu đang sử dụng DocLing hoặc Document AI trực tiếp:

1. **Cấu hình** external API endpoint
2. **Deploy** external service xử lý documents
3. **Test** với document mẫu
4. **Chuyển đổi** production traffic

### Backup Plan

Vẫn có thể sử dụng Document AI service cũ bằng cách:

- Comment external API call
- Uncomment Document AI processing
- Sử dụng `process_document` method

## Examples

### Successful Flow

```
1. Admin uploads "report.pdf" (5MB)
2. File uploaded to: s3://bucket/documents/2024-01-01/abc-123.pdf
3. API called: POST https://api.example.com/process
   Body: {"input": {"url": "https://cdn.example.com/documents/2024-01-01/abc-123.pdf"}}
4. API responds: {"status": "success", "pages": 10, "text_extracted": true}
5. Document status: "completed" with external_response saved
```

### Error Handling

```
1. Admin uploads "large.pdf" (150MB)
2. Error: "File quá lớn. Kích thước tối đa là 100MB"

1. Admin uploads "report.pdf"
2. File uploaded successfully
3. API call timeout after 300s
4. Document status: "failed" with timeout error
```

## Troubleshooting

### Common Issues

**API không response**

- Kiểm tra endpoint URL
- Kiểm tra network connectivity
- Tăng timeout nếu cần

**File upload failed**

- Kiểm tra S3/R2 credentials
- Kiểm tra bucket permissions
- Kiểm tra file size limit

**Permission denied**

- Kiểm tra admin role
- Kiểm tra JWT token validity

### Debug Steps

1. **Check logs** cho upload events
2. **Verify** object storage có file
3. **Test** external API endpoint manual
4. **Check** status response
