# Document Service Guide

## Tổng quan

Document Service là một service mới được thiết kế để xử lý việc upload, chunking và lưu trữ tài liệu vào vector database. Service này sử dụng Google Cloud Document AI để đọc file và Semantic Chunking để chia nhỏ tài liệu một cách thông minh.

## Tính năng chính

### 1. Document Processing với Google Cloud Document AI

- Hỗ trợ đọc nhiều loại file format (PDF, Word, PowerPoint, images, etc.)
- Trích xuất nội dung text và metadata từ documents với độ chính xác cao
- Xử lý bất đồng bộ để không block API calls
- Sử dụng AI model được train sẵn để nhận dạng text từ images và documents

### 2. Semantic Chunking

- Sử dụng `SemanticChunker` thay vì chunking dựa trên số ký tự
- Chia tài liệu dựa trên semantic meaning thay vì kích thước cố định
- Cải thiện chất lượng search và retrieval

### 3. Vector Database Storage

- Lưu trữ chunks vào Pinecone vector database
- Batch processing để tối ưu performance
- Rich metadata cho mỗi chunk

## Cách sử dụng

### Upload Documents

```python
POST /admin/document/store
Content-Type: multipart/form-data

files: List[UploadFile]
```

**Response:**

```json
{
  "documents": [
    {
      "id": "document-uuid",
      "filename": "example.pdf",
      "status": "processing",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

### Kiểm tra trạng thái xử lý

```python
GET /admin/document/status?ids=document-id-1,document-id-2
```

**Response:**

```json
[
  {
    "id": "document-uuid",
    "filename": "example.pdf",
    "status": "completed",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "chunks_count": 25
  }
]
```

### Tìm kiếm documents

```python
GET /admin/document/search?query=machine learning&limit=5&source=example.pdf
```

**Response:**

```json
{
  "query": "machine learning",
  "total_results": 3,
  "results": [
    {
      "content": "Machine learning is a subset of artificial intelligence...",
      "metadata": {
        "source": "example.pdf",
        "document_id": "document-uuid",
        "chunk_index": 5,
        "chunk_type": "semantic"
      },
      "source": "example.pdf",
      "chunk_index": 5
    }
  ]
}
```

### Xem thống kê

```python
GET /admin/document/statistics
```

**Response:**

```json
{
  "total_documents": 10,
  "completed": 8,
  "failed": 1,
  "processing": 1,
  "success_rate": 80.0
}
```

## Cấu hình Semantic Chunking

Service sử dụng các cấu hình sau cho semantic chunking:

```python
semantic_chunker = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=85
)
```

### Các tham số có thể điều chỉnh:

- **breakpoint_threshold_type**: "percentile" hoặc "standard_deviation"
- **breakpoint_threshold_amount**: Ngưỡng để chia chunk (0-100 cho percentile)

## Metadata Structure

Mỗi chunk được lưu với metadata sau:

```json
{
  "source": "filename.pdf",
  "document_id": "unique-document-id",
  "chunk_index": 0,
  "uploaded_at": "2024-01-01T00:00:00.000Z",
  "chunk_type": "semantic",
  "total_chunks": 25
}
```

## Error Handling

Service xử lý các lỗi thường gặp:

1. **File không thể đọc**: Document AI không hỗ trợ format hoặc file bị lỗi
2. **Chunking thất bại**: Không thể tạo chunks meaningful
3. **Vector DB lỗi**: Kết nối hoặc storage issue

Tất cả lỗi đều được log và status được cập nhật thành "failed".

## Performance Considerations

### Batch Processing

- Chunks được lưu theo batch 50 items để tối ưu performance
- Tránh overwhelming vector database

### Async Processing

- File processing được thực hiện bất đồng bộ
- Client nhận response ngay lập tức và có thể check status sau

### Memory Management

- Temporary files được tự động cleanup sau khi xử lý
- File được lưu tại `/tmp/documents/` trước khi xử lý

## Troubleshooting

### Common Issues

1. **"No content could be extracted"**

   - File format không được hỗ trợ bởi DocLing
   - File bị corrupted hoặc password protected

2. **"No meaningful chunks could be created"**

   - Document quá ngắn hoặc không có text content
   - Semantic chunker không thể tìm được breakpoints

3. **"Failed to store chunks in vector database"**
   - Kiểm tra kết nối Pinecone
   - Kiểm tra API key và index configuration

### Monitoring

Sử dụng endpoint `/admin/document/statistics` để monitor:

- Success rate của document processing
- Số lượng documents đang xử lý
- Tổng số documents đã xử lý

## Integration với Existing Code

Service này thay thế code cũ trong `document_router.py` và cung cấp:

1. **Better chunking strategy**: Semantic thay vì character-based
2. **Improved error handling**: Detailed status tracking
3. **Rich metadata**: Thêm thông tin về chunks
4. **Better performance**: Batch processing và async handling
5. **Filtering support**: Tìm kiếm theo source file hoặc document ID

## Dependencies

Service yêu cầu các packages sau:

```
google-cloud-documentai
langchain-experimental>=0.3.0
langchain-openai>=0.2.0
```

Tất cả đã được thêm vào `requirements.txt`.
