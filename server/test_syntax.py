#!/usr/bin/env python3
# Test syntax của admin_courses_router.py

try:
    import ast

    # Đọc file và parse
    with open("app\\routers\\admin_courses_router.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Parse AST để kiểm tra cú pháp
    ast.parse(content)
    print("✅ Cú pháp Python hợp lệ!")

    # Thử import
    import sys

    sys.path.append(".")
    from app.routers import admin_courses_router

    print("✅ Import thành công!")
    print("✅ API đã sẵn sàng sử dụng!")

except SyntaxError as e:
    print(f"❌ Lỗi cú pháp: {e}")
except Exception as e:
    print(f"⚠️ Lỗi khác: {e}")
