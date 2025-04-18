import { NextRequest, NextResponse } from "next/server";

/**
 * Danh sách các đường dẫn công khai, không yêu cầu đăng nhập
 */
export const publicPaths = [
  "/auth/login",
  "/auth/register",
  "/",
  "/about",
  "/courses",
  "/discussions",
];

/**
 * Kiểm tra xem đường dẫn hiện tại có thuộc danh sách công khai không
 * @param {string} path - Đường dẫn cần kiểm tra
 * @returns {boolean} - true nếu đường dẫn là công khai
 */
const isPublicPath = (path: string): boolean => {
  return publicPaths.some((publicPath) => path.startsWith(publicPath));
};

/**
 * Middleware xử lý kiểm tra xác thực cho các đường dẫn
 * @param {NextRequest} request - Yêu cầu Next.js
 * @returns {NextResponse} - Phản hồi Next.js
 */
export function middleware(request: NextRequest) {
  // Lấy đường dẫn hiện tại từ yêu cầu
  const path = request.nextUrl.pathname;

  // Kiểm tra nếu là đường dẫn công khai, cho phép truy cập
  if (isPublicPath(path)) {
    return NextResponse.next();
  }

  // Kiểm tra token xác thực từ cookie
  const token = request.cookies.get("authToken")?.value;

  // Nếu không có token và đường dẫn không công khai, chuyển hướng về trang đăng nhập
  if (!token) {
    // Tạo URL chuyển hướng đến trang đăng nhập
    const loginUrl = new URL("/auth/login", request.url);

    // Thêm URL hiện tại vào tham số callbackUrl để sau khi đăng nhập xong có thể chuyển hướng lại
    loginUrl.searchParams.set("returnUrl", request.nextUrl.pathname);

    return NextResponse.redirect(loginUrl);
  }

  // Nếu có token, cho phép truy cập
  return NextResponse.next();
}

/**
 * Cấu hình middleware để chỉ áp dụng cho một số đường dẫn
 */
export const config = {
  // Áp dụng cho tất cả đường dẫn trừ những đường dẫn tĩnh (static assets)
  matcher: [
    /*
     * Khớp tất cả đường dẫn ngoại trừ:
     * 1. /api (API routes)
     * 2. /_next (Next.js internals)
     * 3. /_static (static files)
     * 4. /_vercel (Vercel internals)
     * 5. /favicon.ico, /sitemap.xml (thường được để ở root)
     */
    "/((?!api|_next|_static|_vercel|favicon.ico|sitemap.xml).*)",
  ],
};
