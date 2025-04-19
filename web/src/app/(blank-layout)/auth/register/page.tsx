"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import TextInput from "@/components/form/TextInput";
import BrandLogo from "@/components/ui/BrandLogo";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

/**
 * Interface cho dữ liệu form đăng ký
 */
interface RegisterFormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

/**
 * Interface cho các lỗi trong form đăng ký
 */
interface RegisterFormErrors {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: string;
  general: string;
}

/**
 * Trang đăng ký tài khoản
 *
 * @returns {React.ReactNode} Component trang đăng ký
 */
export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [formStep, setFormStep] = useState(0);
  const [formData, setFormData] = useState<RegisterFormData>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });
  const [errors, setErrors] = useState<RegisterFormErrors>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: "",
    general: "",
  });

  // App name from environment variable
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "AIGiảiThuật";

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
    const newErrors = {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      agreeToTerms: "",
      general: "",
    };

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = "Họ và tên không được để trống";
      isValid = false;
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Họ và tên phải có ít nhất 2 ký tự";
      isValid = false;
    }

    // Email validation
    if (!formData.email) {
      newErrors.email = "Email không được để trống";
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email không hợp lệ";
      isValid = false;
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Mật khẩu không được để trống";
      isValid = false;
    } else if (formData.password.length < 6) {
      newErrors.password = "Mật khẩu phải có ít nhất 6 ký tự";
      isValid = false;
    } else if (!/(?=.*[A-Za-z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = "Mật khẩu phải chứa ít nhất 1 chữ cái và 1 số";
      isValid = false;
    }

    // Confirm password validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Mật khẩu xác nhận không khớp";
      isValid = false;
    }

    // Terms agreement validation
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = "Bạn phải đồng ý với điều khoản sử dụng";
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
      // Gọi API đăng ký sử dụng tiện ích
      try {
        const tokenData = await api.auth.register({
          email: formData.email,
          password: formData.password,
          fullName: formData.name,
        });

        // Đăng ký thành công, đăng nhập luôn
        await login();

        // Hiển thị thông báo thành công
        setFormStep(1);

        // Chuyển hướng đến trang chủ hoặc return URL sau khoảng thời gian ngắn
        const returnUrl = searchParams.get("returnUrl") || "/";
        setTimeout(() => {
          router.push(returnUrl);
        }, 1500);
      } catch (apiError: any) {
        // Xử lý các lỗi cụ thể từ API
        if (apiError.data?.detail) {
          const errorDetail = apiError.data.detail;
          if (typeof errorDetail === "string") {
            if (errorDetail.includes("Email đã được đăng ký")) {
              setErrors({
                ...errors,
                email:
                  "Email này đã được đăng ký, vui lòng sử dụng email khác.",
                general: "",
              });
            } else if (errorDetail.includes("Tên đăng nhập đã được sử dụng")) {
              setErrors({
                ...errors,
                name: "Tên đăng nhập đã tồn tại, vui lòng chọn tên khác.",
                general: "",
              });
            } else if (errorDetail.includes("Mật khẩu phải có ít nhất")) {
              setErrors({
                ...errors,
                password: errorDetail,
                general: "",
              });
            } else {
              setErrors({
                ...errors,
                general:
                  errorDetail || "Đăng ký thất bại. Vui lòng thử lại sau.",
              });
            }
          } else {
            setErrors({
              ...errors,
              general: "Đăng ký thất bại. Vui lòng thử lại sau.",
            });
          }
        } else {
          setErrors({
            ...errors,
            general:
              apiError.message || "Đăng ký thất bại. Vui lòng thử lại sau.",
          });
        }
      }
    } catch (error) {
      console.error("Lỗi đăng ký:", error);
      setErrors({
        ...errors,
        general: "Lỗi kết nối đến server. Vui lòng thử lại sau.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle social registration
  const handleSocialRegister = (provider: string) => {
    setIsLoading(true);
    console.log(`Đăng ký với ${provider}`);

    // Hiển thị thông báo tính năng đang phát triển
    setErrors({
      ...errors,
      general: `Đăng ký bằng ${provider} đang được phát triển. Vui lòng sử dụng phương thức đăng ký thông thường.`,
    });

    setIsLoading(false);
  };

  // Success step content
  if (formStep === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-background theme-transition">
        <div className="max-w-md w-full space-y-8 bg-background p-8 rounded-xl shadow-lg transition-all duration-300 text-center animate-fade-in">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-primary/10">
            <svg
              className="h-8 w-8 text-primary"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-foreground">
            Đăng ký thành công!
          </h2>
          <p className="mt-2 text-foreground/60">
            Tài khoản của bạn đã được tạo. Bạn sẽ được chuyển đến trang chủ
            trong giây lát.
          </p>
        </div>
      </div>
    );
  }

  // Main registration form
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background theme-transition">
      {/* Form đăng ký bên trái */}
      <div className="w-full md:w-1/2 p-6 flex items-center justify-center bg-background theme-transition">
        <div className="w-full max-w-md space-y-8">
          {/* Logo - Chỉ hiển thị trên màn hình nhỏ */}
          <div className="md:hidden flex justify-center mb-6">
            <BrandLogo variant="theme" size={40} />
          </div>

          <div className="text-center md:text-left">
            <h2 className="text-3xl font-bold text-foreground theme-transition">
              Tạo tài khoản mới
            </h2>
            <p className="mt-2 text-foreground/60 theme-transition">
              Đã có tài khoản?{" "}
              <Link
                href="/auth/login"
                className="font-medium text-primary hover:text-primary/80 transition-colors"
              >
                Đăng nhập ngay
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

          {/* Form đăng ký */}
          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <div className="space-y-4">
              <TextInput
                id="name"
                name="name"
                label="Họ và tên"
                type="text"
                value={formData.name}
                onChange={handleChange}
                error={errors.name}
                autoComplete="name"
                required
              />

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
                autoComplete="new-password"
                required
              />

              <TextInput
                id="confirmPassword"
                name="confirmPassword"
                label="Xác nhận mật khẩu"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={errors.confirmPassword}
                autoComplete="new-password"
                required
              />
            </div>

            {/* Điều khoản sử dụng */}
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="agreeToTerms"
                  name="agreeToTerms"
                  type="checkbox"
                  checked={formData.agreeToTerms}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary/30 transition-colors theme-transition"
                />
              </div>
              <div className="ml-3 text-sm">
                <label
                  htmlFor="agreeToTerms"
                  className={`text-foreground/80 theme-transition ${
                    formData.agreeToTerms ? "font-medium" : ""
                  }`}
                >
                  Tôi đồng ý với{" "}
                  <Link
                    href="/terms"
                    className="text-primary hover:text-primary/80 transition-colors"
                  >
                    Điều khoản sử dụng
                  </Link>{" "}
                  và{" "}
                  <Link
                    href="/privacy"
                    className="text-primary hover:text-primary/80 transition-colors"
                  >
                    Chính sách bảo mật
                  </Link>
                </label>
                {errors.agreeToTerms && (
                  <p className="mt-1 text-red-500 text-xs">
                    {errors.agreeToTerms}
                  </p>
                )}
              </div>
            </div>

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
                  "Đăng ký"
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
                  Hoặc đăng ký với
                </span>
              </div>
            </div>

            {/* Social registration buttons */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleSocialRegister("Google")}
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
                onClick={() => handleSocialRegister("GitHub")}
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

      {/* Bảng thông tin bên phải - Chỉ hiển thị trên màn hình lớn */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-primary to-secondary text-white p-8 flex-col justify-between relative overflow-hidden theme-transition">
        <div className="absolute inset-0 bg-grid-white opacity-10"></div>
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black/30 to-transparent"></div>

        <div className="relative z-10">
          <BrandLogo variant="white" size={48} className="mb-8" />
          <h1 className="text-4xl font-bold mb-6">Bắt đầu hành trình!</h1>
          <p className="text-white/90 text-lg mb-8 max-w-md">
            Tạo tài khoản để khám phá và học tập cùng hệ thống giải thuật thông
            minh tiên tiến nhất hiện nay.
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
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-lg">Học tập hiệu quả</h3>
                <p className="text-white/80">
                  Lộ trình học tập cá nhân hóa, phù hợp với trình độ
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
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-lg">Cộng đồng hỗ trợ</h3>
                <p className="text-white/80">
                  Tham gia cộng đồng học tập với hàng nghìn thành viên
                </p>
              </div>
            </div>
          </div>

          <p className="text-sm text-white/70">
            © {new Date().getFullYear()} {appName}. Mọi quyền được bảo lưu.
          </p>
        </div>
      </div>
    </div>
  );
}
