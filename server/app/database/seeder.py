"""
Module để chạy các seeder cho database

Module này cung cấp các hàm để chạy seeder từ ứng dụng FastAPI
"""

import asyncio
import logging
from typing import List, Optional

from scripts.seed import seed_all

# Thiết lập logging
logger = logging.getLogger(__name__)


async def run_seeder_async(
    seeders: Optional[List[str]] = None, force: bool = False
) -> bool:
    """
    Chạy các seeder được chỉ định

    Args:
        seeders (Optional[List[str]]): Danh sách tên các seeder cần chạy, None để chạy tất cả
        force (bool): Xóa dữ liệu cũ trước khi tạo mới

    Returns:
        bool: True nếu chạy thành công, False nếu có lỗi
    """
    try:
        logger.info(f"Bắt đầu chạy seeders (force={force})...")

        # Chạy seeder trong một thread riêng để không block event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _run_seeders(seeders, force))

        return result
    except Exception as e:
        logger.error(f"Lỗi khi chạy seeders: {str(e)}")
        return False


def _run_seeders(seeders: Optional[List[str]] = None, force: bool = False) -> bool:
    """
    Hàm thực thi các seeder (chạy trong thread riêng)

    Args:
        seeders (Optional[List[str]]): Danh sách tên các seeder cần chạy
        force (bool): Xóa dữ liệu cũ trước khi tạo mới

    Returns:
        bool: True nếu chạy thành công, False nếu có lỗi
    """
    try:
        # Hiện tại chỉ có một seeder duy nhất
        if not seeders or "all" in seeders:
            seed_all()
        else:
            logger.info(f"Chạy các seeders: {seeders}")
            # Có thể mở rộng để chạy từng seeder riêng biệt

        logger.info("Chạy seeders thành công!")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi chạy seeders: {str(e)}")
        return False
