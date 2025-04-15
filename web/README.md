# AI Agent Giải Thuật - Web Frontend

## Yêu cầu hệ thống

- Node.js 18.0.0 trở lên
- pnpm 8.0.0 trở lên

## Các bước cài đặt

1. Cài đặt dependencies:

```bash
pnpm install
```

2. Cấu hình môi trường:

Sao chép file môi trường mẫu:

- Windows:

```bash
copy .env.example .env.local
```

- Linux/Mac:

```bash
cp .env.example .env.local
```

3. Chỉnh sửa các giá trị trong file `.env.local`:

- `NEXT_PUBLIC_API_URL`: URL của backend API
- `NEXT_PUBLIC_API_VERSION`: Version của API
- Các cấu hình khác tùy theo nhu cầu

## Phát triển

Chạy môi trường development:

```bash
pnpm dev
```

Ứng dụng sẽ chạy tại: http://localhost:3000

## Build và Deploy

Build ứng dụng:

```bash
pnpm build
```

Chạy bản production:

```bash
pnpm start
```

## Cấu trúc thư mục

```
web/
├── src/                # Mã nguồn chính
│   ├── app/           # Next.js app router
│   ├── components/    # React components
│   ├── hooks/         # Custom hooks
│   ├── contexts/      # React contexts
│   ├── services/      # API services
│   ├── types/         # TypeScript types
│   └── utils/         # Utility functions
├── public/            # Static files
├── .env.example       # File mẫu cấu hình môi trường
└── package.json       # Project dependencies
```

## Tính năng

- 🔐 Xác thực người dùng
- 🎨 Giao diện người dùng hiện đại với Tailwind CSS
- 🌐 Tích hợp với REST API
- 📱 Responsive design
- 🔍 SEO friendly

## Lưu ý

- Đảm bảo backend API đang chạy trước khi khởi động frontend
- Kiểm tra file `.env.local` đã được cấu hình đúng
- KHÔNG commit file `.env.local` lên git repository
- Sử dụng `NEXT_PUBLIC_` prefix cho các biến môi trường cần được expose ra client-side
