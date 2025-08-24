import os
import uuid
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    Service xử lý việc lưu trữ file trên AWS S3 hoặc Cloudflare R2

    Quy trình upload:
    1. Lưu file tạm thời vào thư mục upload
    2. Upload file từ thư mục tạm thời lên S3
    3. Xóa file tạm thời sau khi upload (thành công hoặc thất bại)
    """

    def __init__(self):
        """
        Khởi tạo service với các thông tin cấu hình từ settings
        """
        # Set retry attempts for S3 connection
        self.RETRY_ATTEMPTS = getattr(settings, 'STORAGE_RETRY_ATTEMPTS', 3)
        
        # Set environment variables để fix lỗi MissingContentLength với boto3 ≥1.36.0
        os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = (
            settings.AWS_REQUEST_CHECKSUM_CALCULATION
        )
        os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = (
            settings.AWS_RESPONSE_CHECKSUM_VALIDATION
        )

        if not settings.S3_ENABLED:
            raise Exception("S3/R2 không được cấu hình đầy đủ.")

        try:
            # Cấu hình client cho S3/R2
            client_config = {
                "aws_access_key_id": settings.S3_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.S3_SECRET_ACCESS_KEY,
                "region_name": settings.S3_REGION,
            }

            # Nếu có endpoint URL (cho Cloudflare R2), thêm vào config
            if settings.S3_ENDPOINT_URL:
                client_config["endpoint_url"] = settings.S3_ENDPOINT_URL

            # retry if cannot connect to s3
            for i in range(self.RETRY_ATTEMPTS):
                try:
                    self.s3_client = boto3.client("s3", **client_config)
                    logger.info("S3 client đã được khởi tạo thành công")
                    break
                except Exception as e:
                    logger.warning(f"Lần thử {i + 1}/{self.RETRY_ATTEMPTS}: Không thể khởi tạo S3 client: {str(e)}")
                    if i < self.RETRY_ATTEMPTS - 1:  # Don't sleep on the last attempt
                        time.sleep(1)
            
            if not self.s3_client:
                raise Exception(f"Không thể khởi tạo S3 client sau {self.RETRY_ATTEMPTS} lần thử")
            self.bucket_name = settings.S3_BUCKET_NAME
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error(f"Không thể khởi tạo S3 client: {str(e)}")
            self.s3_client = None  # Ensure s3_client is None on failure
            raise e

    def _ensure_bucket_exists(self) -> None:
        """
        Kiểm tra xem bucket S3 đã tồn tại chưa. Nếu chưa, tạo bucket và đặt chính sách công khai.
        """
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client hoặc bucket name chưa được cấu hình.")
            return

        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' đã tồn tại.")
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                logger.info(f"Bucket '{self.bucket_name}' không tồn tại. Đang tạo...")
                try:
                    # Tạo bucket
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket '{self.bucket_name}' đã được tạo thành công.")

                    # Đặt chính sách bucket để cho phép đọc công khai
                    bucket_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                            }
                        ],
                    }
                    self.s3_client.put_bucket_policy(
                        Bucket=self.bucket_name, Policy=json.dumps(bucket_policy)
                    )
                    logger.info(
                        f"Chính sách đọc công khai đã được áp dụng cho bucket '{self.bucket_name}'."
                    )
                except ClientError as ce:
                    logger.error(
                        f"Lỗi khi tạo hoặc đặt chính sách cho bucket '{self.bucket_name}': {str(ce)}"
                    )
                    self.s3_client = None
                except Exception as exc:
                    logger.error(
                        f"Lỗi không xác định khi tạo hoặc đặt chính sách cho bucket '{self.bucket_name}': {str(exc)}"
                    )
                    self.s3_client = None
            else:
                logger.error(f"Lỗi khi kiểm tra bucket '{self.bucket_name}': {str(e)}")
                self.s3_client = None
        except Exception as e:
            logger.error(
                f"Lỗi không xác định khi kiểm tra bucket '{self.bucket_name}': {str(e)}"
            )
            self.s3_client = None

    def is_enabled(self) -> bool:
        """
        Kiểm tra xem service có được cấu hình đúng không

        Returns:
            bool: True nếu service được cấu hình đúng
        """
        return self.s3_client is not None

    def _check_service(self) -> None:
        """
        Kiểm tra xem service có được cấu hình đúng không

        Raises:
            HTTPException: Nếu service không được cấu hình đúng
        """
        if not self.is_enabled():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dịch vụ lưu trữ không khả dụng. Vui lòng liên hệ quản trị viên.",
            )

    def _generate_file_key(self, file_prefix: str, filename: str) -> str:
        """
        Tạo key cho file trên S3

        Args:
            file_prefix (str): Prefix của file (thư mục)
            filename (str): Tên file

        Returns:
            str: Key của file trên S3
        """
        # Tạo UUID để đảm bảo tên file là duy nhất
        unique_id = str(uuid.uuid4())

        # Lấy phần mở rộng của file
        _, ext = os.path.splitext(filename)

        # Tạo key với format: prefix/yyyy-mm-dd/uuid.ext
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{file_prefix}{today}/{unique_id}{ext.lower()}"

    def _create_upload_directory(self) -> str:
        """
        Tạo thư mục upload tạm thời nếu chưa tồn tại

        Returns:
            str: Đường dẫn thư mục upload
        """
        upload_dir = settings.UPLOAD_DIR
        Path(upload_dir).mkdir(exist_ok=True)
        return upload_dir

    async def upload_file(
        self, file: UploadFile, prefix: str, metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file lên S3 qua file tạm thời

        Args:
            file (UploadFile): File cần upload
            prefix (str): Prefix của file (thư mục)
            metadata (Optional[Dict[str, str]]): Metadata của file

        Returns:
            Dict[str, Any]: Thông tin file đã upload

        Raises:
            HTTPException: Nếu có lỗi khi upload file
        """
        self._check_service()

        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có file nào được cung cấp",
            )

        # Kiểm tra định dạng file
        content_type = file.content_type
        if not content_type or not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ chấp nhận file hình ảnh",
            )

        # Kiểm tra file size (giới hạn 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File quá lớn. Kích thước tối đa là 10MB",
            )

        # Tạo thư mục upload tạm thời
        upload_dir = self._create_upload_directory()

        # Tạo tên file tạm thời
        temp_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename or '')[1]}"
        temp_file_path = os.path.join(upload_dir, temp_filename)

        try:
            # Tạo key cho file trên S3
            file_key = self._generate_file_key(prefix, file.filename or "")
            logger.info(f"Generated file key: {file_key}")

            # Bước 1: Lưu file tạm thời vào thư mục upload
            logger.info(f"Saving temporary file to: {temp_file_path}")
            file_content = await file.read()
            file_size = len(file_content)

            # Kiểm tra file content không rỗng
            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File không có nội dung",
                )

            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)

            logger.info(
                f"File saved temporarily: {temp_file_path}, size: {file_size} bytes"
            )

            # Bước 2: Upload file từ thư mục tạm thời lên S3
            logger.info(f"Uploading to S3 bucket: {self.bucket_name}")

            # Chuẩn bị ExtraArgs cho upload (set file là public)
            extra_args = {
                "ContentType": content_type,
                "ACL": "public-read",  # Đặt file là public
                "Metadata": metadata or {},
            }

            # Type assertion since _check_service() ensures s3_client is not None
            assert self.s3_client is not None
            self.s3_client.upload_file(
                temp_file_path,
                self.bucket_name,
                file_key,
                ExtraArgs=extra_args,
            )

            logger.info(f"Upload successful for key: {file_key}")

            # Tạo public URL
            public_url = None
            if settings.S3_PUBLIC_URL:
                public_url = f"{settings.S3_PUBLIC_URL.rstrip('/')}/{self.bucket_name}/{file_key}"
            else:
                # Cho Cloudflare R2, URL format khác với AWS S3
                if settings.S3_ENDPOINT_URL:
                    # Cloudflare R2 public URL format
                    endpoint_url = settings.S3_ENDPOINT_URL.replace(
                        ".r2.cloudflarestorage.com", ".r2.dev"
                    )
                    public_url = f"{endpoint_url}/{self.bucket_name}/{file_key}"
                else:
                    # Fallback: sử dụng S3 URL mặc định
                    public_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{file_key}"

            return {
                "key": file_key,
                "url": public_url,
                "content_type": content_type,
                "size": file_size,
            }

        except ClientError as e:
            logger.error(f"Lỗi khi upload file lên S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể upload file: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Lỗi không xác định khi upload file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Đã xảy ra lỗi khi xử lý file",
            )
        finally:
            # Bước 3: Xóa file tạm thời sau khi upload (thành công hoặc thất bại)
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    logger.info(f"Temporary file removed: {temp_file_path}")
            except Exception as e:
                logger.warning(
                    f"Không thể xóa file tạm thời {temp_file_path}: {str(e)}"
                )

            # Reset file position để có thể đọc lại nếu cần
            await file.seek(0)

    async def upload_course_image(
        self, file: UploadFile, course_id: int
    ) -> Dict[str, Any]:
        """
        Upload ảnh khóa học lên S3

        Args:
            file (UploadFile): File ảnh cần upload
            course_id (int): ID của khóa học

        Returns:
            Dict[str, Any]: Thông tin file đã upload
        """
        metadata = {"course_id": str(course_id)}
        return await self.upload_file(file, settings.S3_COURSE_IMAGE_PREFIX, metadata)

    async def upload_user_avatar(
        self, file: UploadFile, user_id: int
    ) -> Dict[str, Any]:
        """
        Upload avatar người dùng lên S3

        Args:
            file (UploadFile): File ảnh cần upload
            user_id (int): ID của người dùng

        Returns:
            Dict[str, Any]: Thông tin file đã upload
        """
        metadata = {"user_id": str(user_id)}
        return await self.upload_file(file, settings.S3_USER_AVATAR_PREFIX, metadata)

    async def upload_document(
        self, file: UploadFile, document_id: str
    ) -> Dict[str, Any]:
        """
        Upload document lên S3 - dành cho tài liệu PDF, DOCX, TXT, etc.

        Args:
            file (UploadFile): File document cần upload
            document_id (str): ID của document

        Returns:
            Dict[str, Any]: Thông tin file đã upload
        """
        self._check_service()

        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có file nào được cung cấp",
            )

        # Kiểm tra định dạng file - cho phép documents
        content_type = file.content_type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "text/plain",
        ]

        if not content_type or content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Định dạng file không được hỗ trợ. Chỉ chấp nhận PDF, DOCX, DOC, TXT và các file ảnh",
            )

        # Kiểm tra file size (giới hạn 100MB cho documents)
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        if hasattr(file, "size") and file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File quá lớn. Kích thước tối đa là 100MB",
            )

        # Tạo thư mục upload tạm thời
        upload_dir = self._create_upload_directory()

        # Tạo tên file tạm thời
        temp_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename or '')[1]}"
        temp_file_path = os.path.join(upload_dir, temp_filename)

        try:
            # Tạo key cho file trên S3
            file_key = self._generate_file_key(
                settings.S3_DOCUMENT_PREFIX, file.filename or ""
            )
            logger.info(f"Generated document file key: {file_key}")

            # Bước 1: Lưu file tạm thời vào thư mục upload
            logger.info(f"Saving temporary document file to: {temp_file_path}")
            file_content = await file.read()
            file_size = len(file_content)

            # Kiểm tra file content không rỗng
            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File không có nội dung",
                )

            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)

            logger.info(
                f"Document file saved temporarily: {temp_file_path}, size: {file_size} bytes"
            )

            # Bước 2: Upload file từ thư mục tạm thời lên S3
            logger.info(f"Uploading document to S3 bucket: {self.bucket_name}")

            # Chuẩn bị ExtraArgs cho upload (không set ACL public vì documents nhạy cảm)
            extra_args = {
                "ContentType": content_type,
                "ACL": "public-read",
                "Metadata": {
                    "document_id": document_id,
                    "uploaded_at": datetime.now().isoformat(),
                },
            }

            # Type assertion since _check_service() ensures s3_client is not None
            assert self.s3_client is not None
            self.s3_client.upload_file(
                temp_file_path,
                self.bucket_name,
                file_key,
                ExtraArgs=extra_args,
            )

            logger.info(f"Document upload successful for key: {file_key}")

            # Tạo public URL (hoặc signed URL cho documents)
            public_url = None
            if settings.S3_PUBLIC_URL:
                public_url = f"{settings.S3_PUBLIC_URL.rstrip('/')}/{self.bucket_name}/{file_key}"
            else:
                # Cho Cloudflare R2, URL format khác với AWS S3
                if settings.S3_ENDPOINT_URL:
                    # Cloudflare R2 public URL format
                    endpoint_url = settings.S3_ENDPOINT_URL.replace(
                        ".r2.cloudflarestorage.com", ".r2.dev"
                    )
                    public_url = f"{endpoint_url}/{self.bucket_name}/{file_key}"
                else:
                    # Fallback: sử dụng S3 URL mặc định
                    public_url = f"https://{self.bucket_name}.s3.{settings.S3_REGION}.amazonaws.com/{file_key}"

            return {
                "key": file_key,
                "url": public_url,
                "content_type": content_type,
                "size": file_size,
                "document_id": document_id,
            }

        except ClientError as e:
            logger.error(f"Lỗi khi upload document lên S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể upload document: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Lỗi không xác định khi upload document: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Đã xảy ra lỗi khi xử lý document",
            )
        finally:
            # Bước 3: Xóa file tạm thời sau khi upload (thành công hoặc thất bại)
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    logger.info(f"Temporary document file removed: {temp_file_path}")
            except Exception as e:
                logger.warning(
                    f"Không thể xóa file tạm thời {temp_file_path}: {str(e)}"
                )

            # Reset file position để có thể đọc lại nếu cần
            await file.seek(0)

    async def delete_file(self, file_key: str) -> bool:
        """
        Xóa file trên S3

        Args:
            file_key (str): Key của file cần xóa

        Returns:
            bool: True nếu xóa thành công

        Raises:
            HTTPException: Nếu có lỗi khi xóa file
        """
        self._check_service()

        try:
            # Type assertion since _check_service() ensures s3_client is not None
            assert self.s3_client is not None
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key,
            )
            return True
        except ClientError as e:
            logger.error(f"Lỗi khi xóa file từ S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể xóa file: {str(e)}",
            )


def get_storage_service() -> StorageService:
    """
    Dependency để inject StorageService

    Returns:
        StorageService: Instance của StorageService
    """
    return StorageService()
