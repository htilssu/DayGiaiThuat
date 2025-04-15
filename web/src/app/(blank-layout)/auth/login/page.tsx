"use client";

import TextInput from "@/components/form/TextInput";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import BrandLogo from "@/components/ui/BrandLogo";
import { useAuth } from "@/contexts/AuthContext";

/**
 * Trang đăng nhập người dùng
 *
 * @returns {React.ReactNode} Component trang đăng nhập
 */
export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [rememberVisible, setRememberVisible] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });
  const [errors, setErrors] = useState({
    email: "",
    password: "",
    general: "",
  });

  // App name from environment variable
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "AIGiảiThuật";

  // Hiệu ứng hiển thị "Ghi nhớ đăng nhập" sau khi người dùng đã nhập liệu
  useEffect(() => {
    if (formData.email || formData.password) {
      setRememberVisible(true);
    }
  }, [formData.email, formData.password]);

  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });

    // Clear error when user types
    if (errors[name as keyof typeof errors]) {
      setErrors({
        ...errors,
        [name]: "",
      });
    }
  };

  // Form validation
  const validateForm = () => {
    let isValid = true;
    const newErrors = { email: "", password: "", general: "" };

    if (!formData.email) {
      newErrors.email = "Email không được để trống";
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email không hợp lệ";
      isValid = false;
    }

    if (!formData.password) {
      newErrors.password = "Mật khẩu không được để trống";
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: formData.email, // API nhận username là email
            password: formData.password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Đăng nhập thất bại");
      }

      // Lưu token và cập nhật context
      if (formData.rememberMe) {
        localStorage.setItem("token", data.access_token);
      } else {
        sessionStorage.setItem("token", data.access_token);
      }

      await login(data.access_token);

      // Redirect to dashboard after successful login
      router.push("/");
    } catch (error: any) {
      console.error("Lỗi đăng nhập:", error);
      setErrors({
        ...errors,
        general:
          error.message ||
          "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle social login
  const handleSocialLogin = (provider: string) => {
    setIsLoading(true);
    console.log(`Đăng nhập với ${provider}`);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      router.push("/");
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background theme-transition">
      {/* Bảng thông tin bên trái - Chỉ hiển thị trên màn hình lớn */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-primary to-secondary text-white p-8 flex-col justify-between relative overflow-hidden theme-transition">
        <div className="absolute inset-0 bg-grid-white opacity-10"></div>
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black/30 to-transparent"></div>

        <div className="relative z-10">
          <BrandLogo variant="white" size={48} className="mb-8" />
          <h1 className="text-4xl font-bold mb-6">Chào mừng trở lại!</h1>
          <p className="text-white/90 text-lg mb-8 max-w-md">
            Đăng nhập để tiếp tục hành trình khám phá và chinh phục thế giới
            thuật toán cùng cộng đồng học tập.
          </p>
        </div>

        <div className="relative z-10">
          <div className="mb-8">
            <div className="flex items-center mb-6">
              <div className="h-12 w-12 bg-white/20 rounded-full flex items-center justify-center mr-4">
                <svg
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-lg">Bảo mật cao</h3>
                <p className="text-white/80">
                  Dữ liệu của bạn luôn được bảo vệ an toàn
                </p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="h-12 w-12 bg-white/20 rounded-full flex items-center justify-center mr-4">
                <svg
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-lg">Trải nghiệm cá nhân hóa</h3>
                <p className="text-white/80">
                  Nội dung được điều chỉnh theo trình độ của bạn
                </p>
              </div>
            </div>
          </div>

          <p className="text-sm text-white/70">
            © {new Date().getFullYear()} {appName}. Mọi quyền được bảo lưu.
          </p>
        </div>
      </div>

      {/* Form đăng nhập bên phải */}
      <div className="w-full md:w-1/2 p-6 flex items-center justify-center bg-background theme-transition">
        <div className="w-full max-w-md space-y-8">
          {/* Logo - Chỉ hiển thị trên màn hình nhỏ */}
          <div className="md:hidden flex justify-center mb-6">
            <BrandLogo variant="theme" size={40} />
          </div>

          <div className="text-center md:text-left">
            <h2 className="text-3xl font-bold text-foreground theme-transition">
              Đăng nhập
            </h2>
            <p className="mt-2 text-foreground/60 theme-transition">
              Chưa có tài khoản?{" "}
              <Link
                href="/auth/register"
                className="font-medium text-primary hover:text-primary/80 transition-colors"
              >
                Đăng ký ngay
              </Link>
            </p>
          </div>

          {/* Thông báo lỗi chung */}
          {errors.general && (
            <div
              className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg relative theme-transition"
              role="alert"
            >
              <span className="block sm:inline">{errors.general}</span>
            </div>
          )}

          {/* Form đăng nhập */}
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <div className="space-y-4">
              <TextInput
                id="email"
                name="email"
                label="Email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                autoComplete="email"
                required
              />

              <TextInput
                id="password"
                name="password"
                label="Mật khẩu"
                type="password"
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                autoComplete="current-password"
                required
              />
            </div>

            {/* Remember me và Quên mật khẩu */}
            <div
              className={`flex items-center justify-between transition-opacity duration-300 ${
                rememberVisible ? "opacity-100" : "opacity-0"
              }`}
            >
              <div className="flex items-center">
                <input
                  id="rememberMe"
                  name="rememberMe"
                  type="checkbox"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary/30 transition-colors theme-transition"
                />
                <label
                  htmlFor="rememberMe"
                  className={`ml-2 block text-sm text-foreground/80 theme-transition ${
                    formData.rememberMe ? "font-medium" : ""
                  }`}
                >
                  Ghi nhớ đăng nhập
                </label>
              </div>
              <div className="text-sm">
                <Link
                  href="/auth/forgot-password"
                  className="font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Quên mật khẩu?
                </Link>
              </div>
            </div>

            {/* Submit button */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent rounded-lg text-white btn-gradient-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/50 shadow-sm hover:shadow-md transition-all duration-200"
              >
                {isLoading ? (
                  <svg
                    className="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                ) : (
                  "Đăng nhập"
                )}
              </button>
            </div>

            {/* Divider */}
            <div className="mt-6 relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-foreground/10 theme-transition"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-background text-foreground/40 theme-transition">
                  Hoặc đăng nhập với
                </span>
              </div>
            </div>

            {/* Social login buttons */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleSocialLogin("Google")}
                className="w-full inline-flex justify-center py-2.5 px-4 border border-foreground/10 rounded-lg shadow-sm bg-background text-sm font-medium text-foreground hover:bg-foreground/5 transition-colors theme-transition"
              >
                <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <g transform="matrix(1, 0, 0, 1, 27.009001, -39.238998)">
                    <path
                      fill="#4285F4"
                      d="M -3.264 51.509 C -3.264 50.719 -3.334 49.969 -3.454 49.239 L -14.754 49.239 L -14.754 53.749 L -8.284 53.749 C -8.574 55.229 -9.424 56.479 -10.684 57.329 L -10.684 60.329 L -6.824 60.329 C -4.564 58.239 -3.264 55.159 -3.264 51.509 Z"
                    />
                    <path
                      fill="#34A853"
                      d="M -14.754 63.239 C -11.514 63.239 -8.804 62.159 -6.824 60.329 L -10.684 57.329 C -11.764 58.049 -13.134 58.489 -14.754 58.489 C -17.884 58.489 -20.534 56.379 -21.484 53.529 L -25.464 53.529 L -25.464 56.619 C -23.494 60.539 -19.444 63.239 -14.754 63.239 Z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M -21.484 53.529 C -21.734 52.809 -21.864 52.039 -21.864 51.239 C -21.864 50.439 -21.724 49.669 -21.484 48.949 L -21.484 45.859 L -25.464 45.859 C -26.284 47.479 -26.754 49.299 -26.754 51.239 C -26.754 53.179 -26.284 54.999 -25.464 56.619 L -21.484 53.529 Z"
                    />
                    <path
                      fill="#EA4335"
                      d="M -14.754 43.989 C -12.984 43.989 -11.404 44.599 -10.154 45.789 L -6.734 42.369 C -8.804 40.429 -11.514 39.239 -14.754 39.239 C -19.444 39.239 -23.494 41.939 -25.464 45.859 L -21.484 48.949 C -20.534 46.099 -17.884 43.989 -14.754 43.989 Z"
                    />
                  </g>
                </svg>
                Google
              </button>
              <button
                type="button"
                onClick={() => handleSocialLogin("GitHub")}
                className="w-full inline-flex justify-center py-2.5 px-4 border border-foreground/10 rounded-lg shadow-sm bg-background text-sm font-medium text-foreground hover:bg-foreground/5 transition-colors theme-transition"
              >
                <svg
                  className="h-5 w-5 mr-2"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                GitHub
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
