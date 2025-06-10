#!/usr/bin/env python
"""
Script để chạy tất cả các test với coverage report.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_tests():
    """
    Chạy tất cả các test với pytest và tạo báo cáo coverage.
    """
    # Đảm bảo chạy từ thư mục gốc của dự án
    os.chdir(Path(__file__).parent.parent)

    print("Đang chạy tests với coverage report...")

    # Chạy pytest với coverage
    result = subprocess.run(
        [
            "pytest",
            "-v",
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:coverage_html",
            "tests/",
        ],
        capture_output=False,
    )

    if result.returncode != 0:
        print("Có lỗi khi chạy tests!")
        sys.exit(result.returncode)

    print("\nTests hoàn thành thành công!")
    print("Báo cáo coverage HTML đã được tạo trong thư mục 'coverage_html'")


if __name__ == "__main__":
    run_tests()
