"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import TextInput from "@/components/form/TextInput";

/**
 * Trang đăng ký tài khoản
 *
 * @returns {JSX.Element} Component trang đăng ký
 */
export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formStep, setFormStep] = useState(0); // For multi-step form experience
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });
  const [errors, setErrors] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: "",
    general: "",
  });

  // State for showing animation when entering data
  const [formFocused, setFormFocused] = useState(false);

  // App name from environment variable
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "AIGiảiThuật";

  useEffect(() => {
    if (
      formData.name ||
      formData.email ||
      formData.password ||
      formData.confirmPassword
    ) {
      setFormFocused(true);
    }
  }, [
    formData.name,
    formData.email,
    formData.password,
    formData.confirmPassword,
  ]);

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
      // Simulating API call
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Replace with actual registration logic
      console.log("Đăng ký với:", formData);

      // Show success message and redirect
      setFormStep(1); // Move to success step

      // Redirect to login after delay
      setTimeout(() => {
        router.push("/auth/login");
      }, 3000);
    } catch (error) {
      console.error("Lỗi đăng ký:", error);
      setErrors({
        ...errors,
        general: "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle social registration
  const handleSocialRegister = (provider: string) => {
    setIsLoading(true);
    console.log(`Đăng ký với ${provider}`);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setFormStep(1);
      // Redirect to login after delay
      setTimeout(() => {
        router.push("/auth/login");
      }, 3000);
    }, 1000);
  };

  // Success step content
  if (formStep === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-white to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
        <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg transition-all duration-300 text-center animate-fade-in">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-900">
            <svg
              className="h-8 w-8 text-emerald-600 dark:text-emerald-300"
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
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-gray-100">
            Đăng ký thành công!
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-300">
            Tài khoản của bạn đã được tạo. Bạn sẽ được chuyển hướng đến trang
            đăng nhập trong vài giây.
          </p>
          <div className="mt-5">
            <div className="relative pt-1">
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-emerald-200 dark:bg-emerald-900">
                <div
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-emerald-500 dark:bg-emerald-400 animate-pulse"
                  style={{ width: "100%" }}
                ></div>
              </div>
            </div>
            <Link
              href="/auth/login"
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-700 dark:hover:bg-emerald-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 mt-4"
            >
              Đi đến đăng nhập
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Bảng thông tin bên trái - Chỉ hiển thị trên màn hình lớn */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-emerald-600 to-amber-500 dark:from-emerald-800 dark:to-amber-700 text-white p-8 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 bg-grid-white/[0.05] opacity-10"></div>
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-black/30 to-transparent"></div>

        <div className="relative z-10">
          <div className="flex items-center mb-8">
            <div className="h-10 w-10 bg-white rounded-lg flex items-center justify-center text-emerald-600 font-bold shadow-md mr-3">
              <span className="text-lg">A</span>
            </div>
            <span className="font-bold text-2xl">{appName}</span>
          </div>
          <h1 className="text-4xl font-bold mb-6">Tham gia cộng đồng!</h1>
          <p className="text-white/90 text-lg mb-8 max-w-md">
            Đăng ký tài khoản để bắt đầu hành trình khám phá thế giới thuật toán
            và kết nối với cộng đồng người học.
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
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-lg">Học tập cá nhân hóa</h3>
                <p className="text-white/80">
                  Nội dung được điều chỉnh theo trình độ và sở thích của bạn
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
                <h3 className="font-medium text-lg">Cộng đồng học tập</h3>
                <p className="text-white/80">
                  Kết nối và học hỏi từ những người có cùng đam mê
                </p>
              </div>
            </div>
          </div>

          <p className="text-sm text-white/70">
            © {new Date().getFullYear()} {appName}. Mọi quyền được bảo lưu.
          </p>
        </div>
      </div>

      {/* Form đăng ký bên phải */}
      <div className="w-full md:w-1/2 p-6 flex items-center justify-center bg-white dark:bg-gray-900">
        <div
          className={`w-full max-w-md space-y-8 ${
            formFocused ? "animate-slide-up" : ""
          }`}
        >
          {/* Logo - Chỉ hiển thị trên màn hình nhỏ */}
          <div className="md:hidden flex justify-center mb-6">
            <div className="flex items-center">
              <div className="h-10 w-10 bg-gradient-to-br from-emerald-600 to-amber-500 rounded-lg flex items-center justify-center text-white font-bold shadow-md mr-3">
                <span className="text-lg">A</span>
              </div>
              <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-amber-500 dark:from-emerald-400 dark:to-amber-300">
                {appName}
              </span>
            </div>
          </div>

          <div className="text-center md:text-left">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              Đăng ký tài khoản
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Đã có tài khoản?{" "}
              <Link
                href="/auth/login"
                className="font-medium text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300 transition-colors"
              >
                Đăng nhập ngay
              </Link>
            </p>
          </div>

          {/* Thông báo lỗi chung */}
          {errors.general && (
            <div
              className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg relative"
              role="alert"
            >
              <span className="block sm:inline">{errors.general}</span>
            </div>
          )}

          {/* Form đăng ký */}
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {/* Name input with TextInput component */}
            <TextInput
              id="name"
              name="name"
              label="Họ và tên"
              type="text"
              value={formData.name}
              onChange={handleChange}
              error={errors.name}
              required
            />

            {/* Email input with TextInput component */}
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

            {/* Password input with TextInput component */}
            <div>
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
                showPasswordToggle
              />

              {formData.password && !errors.password && (
                <div className="mt-2">
                  <div className="flex space-x-1">
                    <div
                      className={`h-1 w-1/3 rounded-full ${
                        formData.password.length >= 6
                          ? "bg-emerald-400"
                          : "bg-gray-300 dark:bg-gray-600"
                      }`}
                    ></div>
                    <div
                      className={`h-1 w-1/3 rounded-full ${
                        formData.password.length >= 8
                          ? "bg-emerald-400"
                          : "bg-gray-300 dark:bg-gray-600"
                      }`}
                    ></div>
                    <div
                      className={`h-1 w-1/3 rounded-full ${
                        /(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])/.test(
                          formData.password
                        )
                          ? "bg-emerald-400"
                          : "bg-gray-300 dark:bg-gray-600"
                      }`}
                    ></div>
                  </div>
                  <p className="text-xs mt-1 text-gray-500 dark:text-gray-400">
                    Mật khẩu mạnh nên có ít nhất 8 ký tự và bao gồm chữ cái, số
                    và ký tự đặc biệt
                  </p>
                </div>
              )}
            </div>

            {/* Confirm password input with TextInput component */}
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
              showPasswordToggle
            />

            {/* Terms and conditions agreement */}
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="agreeToTerms"
                  name="agreeToTerms"
                  type="checkbox"
                  checked={formData.agreeToTerms}
                  onChange={handleChange}
                  className={`h-4 w-4 text-emerald-600 focus:ring-emerald-500 border-gray-300 rounded transition-colors ${
                    errors.agreeToTerms ? "border-red-500" : ""
                  }`}
                />
              </div>
              <div className="ml-3 text-sm">
                <label
                  htmlFor="agreeToTerms"
                  className="font-medium text-gray-700 dark:text-gray-300"
                >
                  Tôi đồng ý với
                  <Link
                    href="/dieu-khoan"
                    className="ml-1 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    Điều khoản sử dụng
                  </Link>{" "}
                  và{" "}
                  <Link
                    href="/chinh-sach"
                    className="text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
                  >
                    Chính sách bảo mật
                  </Link>
                </label>
                {errors.agreeToTerms && (
                  <p className="mt-1 text-sm text-red-500 dark:text-red-400">
                    {errors.agreeToTerms}
                  </p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-700 dark:hover:bg-emerald-600 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="absolute left-0 inset-y-0 flex items-center pl-3">
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
                    <svg
                      className="h-5 w-5 text-emerald-200 group-hover:text-emerald-100"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </span>
                {isLoading ? "Đang xử lý..." : "Đăng ký ngay"}
              </button>
            </div>
          </form>

          {/* Divider */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-gray-700"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400">
                  Hoặc đăng ký với
                </span>
              </div>
            </div>

            {/* Social login buttons */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleSocialRegister("Google")}
                disabled={isLoading}
                className="w-full inline-flex justify-center py-2.5 px-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <svg
                  className="h-5 w-5 mr-2"
                  viewBox="0 0 24 24"
                  width="24"
                  height="24"
                  xmlns="http://www.w3.org/2000/svg"
                >
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
                <span>Google</span>
              </button>
              <button
                type="button"
                onClick={() => handleSocialRegister("Facebook")}
                disabled={isLoading}
                className="w-full inline-flex justify-center py-2.5 px-4 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <svg
                  className="h-5 w-5 mr-2 text-[#1877F2]"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                  width="24"
                  height="24"
                >
                  <path d="M12.001 2C6.47813 2 2.00098 6.47715 2.00098 12C2.00098 16.9913 5.65783 21.1283 10.4385 21.8785V14.8906H7.89941V12H10.4385V9.79688C10.4385 7.29063 11.9314 5.90625 14.2156 5.90625C15.3097 5.90625 16.4541 6.10156 16.4541 6.10156V8.5625H15.1931C13.9509 8.5625 13.5635 9.33334 13.5635 10.1242V12H16.3369L15.8936 14.8906H13.5635V21.8785C18.3441 21.1283 22.001 16.9913 22.001 12C22.001 6.47715 17.5238 2 12.001 2Z" />
                </svg>
                <span>Facebook</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
