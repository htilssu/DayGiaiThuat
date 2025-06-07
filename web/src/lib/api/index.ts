/**
 * Module tổng hợp và export tất cả các API module
 * @module api
 */

import authApi from "./auth";
import userApi from "./user";
import coursesApi from "./courses";
import chatApi from "./chat";

// Export các module API
const api = {
  auth: authApi,
  user: userApi,
  courses: coursesApi,
  chat: chatApi,
  // Thêm các module API khác tại đây, ví dụ:
  // product: productApi,
  // ...
};

// Export các hàm tiện ích từ client để sử dụng trực tiếp nếu cần
export * from "./client";

// Export type từ các module
export * from "./auth";
export * from "./user";
export * from "./courses";
export * from "./chat";

export default api;
