"use client";

/**
 * Props cho BrandLogo component
 * @interface BrandLogoProps
 * @property {string} [className] - Class CSS bổ sung
 * @property {number} [size=40] - Kích thước logo (px)
 * @property {boolean} [withText=true] - Hiển thị text bên cạnh logo
 * @property {'primary' | 'white' | 'theme'} [variant='primary'] - Biến thể màu sắc của logo
 */
interface BrandLogoProps {
  className?: string;
  size?: number;
  withText?: boolean;
  variant?: "primary" | "white" | "theme";
}

/**
 * Component hiển thị logo thương hiệu
 *
 * @param {BrandLogoProps} props - Props cho component
 * @returns {React.ReactElement} SVG logo của thương hiệu
 */
export default function BrandLogo({
  className = "",
  size = 40,
  withText = true,
  variant = "primary",
}: BrandLogoProps): React.ReactElement {
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "AIGiảiThuật";

  // Xác định màu sắc dựa trên variant và theme

  return (
    <div className={`flex items-center ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="mr-3"
      >
        {/* Hình nền tròn với gradient */}
        <circle cx="50" cy="50" r="50" fill="url(#brandGradient)" />

        {/* Chữ A stylized */}
        <path
          d="M37 70L50 30L63 70H53L50 63L47 70H37Z"
          fill="white"
          strokeWidth="2"
        />

        {/* Định nghĩa gradient */}
        <defs>
          <linearGradient
            id="brandGradient"
            x1="0"
            y1="0"
            x2="100"
            y2="100"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#f59e0b" />
          </linearGradient>
        </defs>
      </svg>

      {withText && (
        <span
          className={`font-bold text-xl ${
            variant === "theme"
              ? "text-gradient-theme"
              : variant === "white"
              ? "text-white"
              : ""
          }`}
        >
          {appName}
        </span>
      )}
    </div>
  );
}
