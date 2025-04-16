import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Hàm kết hợp các class CSS với Tailwind
 * @param inputs - Danh sách các class cần kết hợp
 * @returns string - Chuỗi class đã được kết hợp và tối ưu
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
