import os
import requests

# Tạo thư mục static nếu chưa tồn tại
os.makedirs("static", exist_ok=True)

# URLs của các file cần tải
files = {
    "swagger-ui-bundle.js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
    "swagger-ui.css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    "redoc.standalone.js": "https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
    "favicon.png": "https://fastapi.tiangolo.com/img/favicon.png"
}

# Tải và lưu từng file
for filename, url in files.items():
    print(f"Đang tải {filename}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join("static", filename), "wb") as f:
            f.write(response.content)
        print(f"✓ Đã tải xong {filename}")
    else:
        print(f"✗ Lỗi khi tải {filename}: {response.status_code}")

print("\nHoàn thành!") 