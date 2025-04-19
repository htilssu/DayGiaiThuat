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

/**
 * Chuyển đổi chuỗi từ dạng snake_case sang camelCase
 * @param str - Chuỗi cần chuyển đổi
 * @returns string - Chuỗi đã được chuyển sang camelCase
 */
export function toCamelCase(str: string): string {
  return str.replace(/([-_][a-z])/g, (group) =>
    group.toUpperCase().replace("-", "").replace("_", "")
  );
}

/**
 * Chuyển đổi một object từ snake_case sang camelCase một cách đệ quy
 * @param obj - Object cần chuyển đổi
 * @returns - Object đã được chuyển đổi sang camelCase
 */
export function transformToCamelCase<T>(obj: any): T {
  if (Array.isArray(obj)) {
    return obj.map(transformToCamelCase) as any;
  }
  
  if (obj !== null && typeof obj === "object") {
    const camelCaseObj: Record<string, any> = {};
    
    Object.keys(obj).forEach((key) => {
      const camelKey = toCamelCase(key);
      camelCaseObj[camelKey] = transformToCamelCase(obj[key]);
    });
    
    return camelCaseObj as T;
  }
  
  return obj as T;
}
