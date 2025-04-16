/**
 * Module tổng hợp và export tất cả các API module
 * @module api
 */

import authApi from "./auth";
import userApi from "./user";

// Export các module API
const api = {
  auth: authApi,
  user: userApi,
  // Thêm các module API khác tại đây, ví dụ:
  // product: productApi,
  // ...
};

// Export các hàm tiện ích từ client để sử dụng trực tiếp nếu cần
export * from "./client";

// Export type từ các module
export * from "./auth";
export * from "./user";

export default api;
