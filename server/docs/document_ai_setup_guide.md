# Hướng dẫn Setup Google Cloud Document AI

## Tổng quan

Google Cloud Document AI được sử dụng để thay thế DocLing trong việc xử lý và trích xuất nội dung từ documents (PDF, images, v.v.). Document AI cung cấp độ chính xác cao hơn và hỗ trợ nhiều định dạng file hơn.

## Yêu cầu

- Google Cloud Platform account
- Project đã enable Document AI API
- Service Account với quyền Document AI User
- Processor đã được tạo sẵn

## Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Ghi nhớ Project ID để cấu hình

## Bước 2: Enable Document AI API

1. Trong Google Cloud Console, mở **APIs & Services > Library**
2. Tìm kiếm "Document AI API"
3. Click **Enable** để kích hoạt API

## Bước 3: Tạo Service Account

1. Mở **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Nhập thông tin:
   - Name: `document-ai-service`
   - Description: `Service account for Document AI processing`
4. Click **Create and Continue**
5. Thêm role: **Document AI API User**
6. Click **Done**

## Bước 4: Tạo và Download Key

1. Click vào service account vừa tạo
2. Chuyển qua tab **Keys**
3. Click **Add Key > Create new key**
4. Chọn **JSON** format
5. Download file JSON và lưu an toàn

## Bước 5: Tạo Document AI Processor

1. Mở **Document AI > Overview**
2. Click **Create Processor**
3. Chọn processor type:
   - **Document OCR**: Cho việc OCR cơ bản
   - **Form Parser**: Cho documents có cấu trúc
   - **Specialized Processors**: Cho các loại document cụ thể
4. Chọn **Region** (recommend: `us` hoặc `eu`)
5. Nhập **Processor Name**
6. Click **Create**
7. Ghi nhớ **Processor ID** từ URL hoặc details page

## Bước 6: Cấu hình Authentication

### Cách 1: Sử dụng Service Account Key File

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### Cách 2: Sử dụng gcloud CLI (recommended for development)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login và set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Tạo application default credentials
gcloud auth application-default login
```

## Bước 7: Cấu hình Environment Variables

Cập nhật file `.env`:

```env
# Google Cloud Document AI
GOOGLE_CLOUD_PROJECT_ID=your-project-id
DOCUMENT_AI_LOCATION=us  # hoặc eu
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
```

## Bước 8: Test Configuration

Tạo file test để kiểm tra:

```python
# test_document_ai.py
from app.services.document_ai_service import document_ai_service

# Test với một file PDF
try:
    documents = document_ai_service.load_documents("path/to/test.pdf")
    print(f"Successfully processed {len(documents)} documents")
    for i, doc in enumerate(documents):
        print(f"Document {i}: {len(doc.page_content)} characters")
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### Lỗi Authentication

```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Giải pháp:**

- Kiểm tra GOOGLE_APPLICATION_CREDENTIALS environment variable
- Chạy `gcloud auth application-default login`
- Kiểm tra service account key file có tồn tại

### Lỗi Permission Denied

```
403 The caller does not have permission
```

**Giải pháp:**

- Kiểm tra service account có role Document AI API User
- Kiểm tra Document AI API đã được enable
- Kiểm tra project ID đúng

### Lỗi Processor Not Found

```
404 Processor not found
```

**Giải pháp:**

- Kiểm tra DOCUMENT_AI_PROCESSOR_ID đúng
- Kiểm tra processor tồn tại trong project và region
- Kiểm tra DOCUMENT_AI_LOCATION đúng

### Lỗi Quota Exceeded

```
429 Quota exceeded
```

**Giải pháp:**

- Kiểm tra quota limits trong Console
- Request increase quota nếu cần
- Implement retry logic với exponential backoff

## Supported File Types

Document AI hỗ trợ các định dạng sau:

- **PDF**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`
- **Microsoft Word**: `.doc`, `.docx`
- **Text**: `.txt`

## File Size Limits và Fallback Methods

### Giới hạn kích thước Document AI

Google Cloud Document AI có giới hạn **40MB** cho mỗi document. Để xử lý file lớn hơn, hệ thống sẽ tự động sử dụng fallback methods:

### Fallback Methods

#### 1. PDF Files (PyPDF2)

- **Kích hoạt**: Khi file PDF > 40MB
- **Thư viện**: PyPDF2
- **Tính năng**: Trích xuất text từng page
- **Metadata**: `processor: "pypdf2_fallback"`

#### 2. DOCX Files (python-docx)

- **Kích hoạt**: Khi file DOCX > 40MB
- **Thư viện**: python-docx
- **Tính năng**: Trích xuất text từ paragraphs
- **Metadata**: `processor: "python-docx_fallback"`

#### 3. Text Files

- **Kích hoạt**: Khi file TXT > 40MB
- **Phương pháp**: Đọc trực tiếp file
- **Metadata**: `processor: "text_fallback"`

### Installation Requirements cho Fallback

```bash
pip install PyPDF2 python-docx
```

### Example Error Messages

```
File quá lớn (93.3MB > 40.0MB), sử dụng fallback method...
```

### Fallback Metadata Structure

```python
{
    "source": "large_document.pdf",
    "source_type": "pdf_fallback",
    "processor": "pypdf2_fallback",
    "page_number": 1,
    "total_pages": 150
}
```

## Best Practices

### 1. File Size Optimization

- **Recommended**: Giới hạn file size < 20MB cho performance tốt
- **Maximum Document AI**: 40MB (auto fallback methods cho file lớn hơn)
- Sử dụng PDF compression cho files lớn
- Chia nhỏ documents rất lớn (>100MB) trước khi upload
- Fallback methods có thể chậm hơn và ít chính xác hơn Document AI

### 2. Error Handling

- Implement retry logic cho transient errors
- Log errors chi tiết để debugging
- Fallback mechanism khi Document AI không available

### 3. Cost Optimization

- Monitor usage trong Billing dashboard
- Sử dụng appropriate processor type
- Cache results khi có thể

### 4. Security

- Không commit service account keys vào repository
- Sử dụng environment variables hoặc secret management
- Rotate keys định kỳ

## Monitoring và Logging

### Cloud Logging

Xem logs trong Google Cloud Console:

```
resource.type="cloud_function" OR resource.type="gce_instance"
labels."service_name"="document-ai"
```

### Metrics

Monitor các metrics quan trọng:

- Request count
- Error rate
- Latency
- Cost per request

## Migration từ DocLing

### Changes Made

1. Thay thế `langchain-docling` bằng `google-cloud-documentai`
2. Tạo `DocumentAIService` class
3. Cập nhật `DocumentService` để sử dụng Document AI
4. Thêm rich metadata cho processed documents

### Benefits

- **Độ chính xác cao hơn**: AI-powered OCR
- **Hỗ trợ nhiều formats**: Images, các loại documents
- **Scalable**: Google Cloud infrastructure
- **Rich metadata**: Page-level information, layout detection

### Breaking Changes

- Cần Google Cloud setup
- Metadata structure thay đổi
- API response format khác

## Cost Estimation

Document AI pricing (tham khảo, có thể thay đổi):

- Document OCR: $1.50 per 1,000 pages
- Form Parser: $50.00 per 1,000 pages
- Specialized Processors: varies

Estimate chi phí dựa trên volume processing để budget phù hợp.

## Support và Documentation

- [Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Client Libraries](https://cloud.google.com/document-ai/docs/libraries)
- [Best Practices](https://cloud.google.com/document-ai/docs/best-practices)
- [Pricing](https://cloud.google.com/document-ai/pricing)
