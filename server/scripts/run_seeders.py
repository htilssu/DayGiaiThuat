"""
Script để chạy các seeder khi ứng dụng khởi động

Script này sẽ được gọi từ main.py khi cờ RUN_SEEDERS_ON_STARTUP được bật
"""

import logging
from typing import List, Optional

from app.core.config import settings
from scripts.seed import seed_all

# Thiết lập logging
logger = logging.getLogger(__name__)


def run_seeders() -> bool:
    """
    Chạy các seeder được cấu hình trong settings

    Returns:
        bool: True nếu chạy thành công, False nếu có lỗi
    """
    try:
        logger.info("Bắt đầu chạy seeders...")

        # Nếu không có danh sách seeders cụ thể, chạy tất cả
        if not settings.SEEDERS_TO_RUN:
            logger.info("Chạy tất cả seeders")
            seed_all()
        else:
            logger.info(f"Chạy các seeders: {settings.SEEDERS_TO_RUN}")
            # Có thể mở rộng để chạy từng seeder riêng biệt
            # Hiện tại chỉ có một seeder duy nhất
            if "all" in settings.SEEDERS_TO_RUN:
                seed_all()

        logger.info("Chạy seeders thành công!")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi chạy seeders: {str(e)}")
        return False
