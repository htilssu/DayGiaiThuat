import os
import uuid
from typing import Optional, Dict, Any
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    Service xử lý việc lưu trữ file trên AWS S3
    """

    def __init__(self):
        """
        Khởi tạo service với các thông tin cấu hình từ settings
        """
        if not settings.S3_ENABLED:
            logger.warning(
                "S3 không được cấu hình đầy đủ. Các tính năng upload sẽ không hoạt động."
            )
            self.s3_client = None
            return

        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        except Exception as e:
            logger.error(f"Không thể khởi tạo S3 client: {str(e)}")
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

    async def upload_file(
        self, file: UploadFile, prefix: str, metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file lên S3

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

        try:
            # Tạo key cho file
            file_key = self._generate_file_key(prefix, file.filename)

            # Upload file lên S3
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=metadata or {},
            )

            # Tạo public URL nếu có cấu hình
            public_url = None
            if settings.S3_PUBLIC_URL:
                public_url = f"{settings.S3_PUBLIC_URL.rstrip('/')}/{file_key}"
            else:
                # Sử dụng S3 URL mặc định
                public_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

            return {
                "key": file_key,
                "url": public_url,
                "content_type": content_type,
                "size": len(file_content),
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
