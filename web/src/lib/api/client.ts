/**
 * Module chứa các cấu hình và phương thức gọi API cơ bản
 * @module api/client
 */

import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios";

/**
 * URL cơ sở của API
 */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Phiên bản API
 */
export const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || "/api/v1";

/**
 * URL đầy đủ của API bao gồm URL cơ sở và phiên bản
 */
export const BASE_URL = `${API_URL}${API_VERSION}`;

/**
 * Tên cookie lưu JWT token
 */
export const TOKEN_COOKIE_NAME =
  process.env.NEXT_PUBLIC_TOKEN_COOKIE_NAME || "access_token";

/**
 * Trình xử lý lỗi mặc định cho các yêu cầu API
 * @param error - Lỗi từ Axios
 * @returns Object chứa thông tin lỗi chuẩn hóa
 */
export const handleApiError = (error: AxiosError) => {
  if (error.response) {
    // Phản hồi từ server với mã trạng thái nằm ngoài phạm vi 2xx
    const responseData = error.response.data as any;

    // Lấy thông báo lỗi chi tiết từ server nếu có
    let errorMessage = "Lỗi phản hồi từ server";

    if (responseData) {
      console.log(responseData);
      if (responseData.detail) {
        // FastAPI thường trả về lỗi trong trường 'detail'
        errorMessage =
          typeof responseData.detail === "string"
            ? responseData.detail
            : JSON.stringify(responseData.detail);
      } else if (responseData.message) {
        // Hoặc trường 'message'
        errorMessage = responseData.message;
      } else if (typeof responseData === "string") {
        // Nếu responseData là string
        errorMessage = responseData;
      }
    }

    return {
      status: error.response.status,
      data: error.response.data,
      message: errorMessage,
    };
  } else if (error.request) {
    // Yêu cầu đã được thực hiện nhưng không nhận được phản hồi
    return {
      status: 0,
      data: null,
      message: "Không nhận được phản hồi từ server",
    };
  } else {
    // Có lỗi khi thiết lập yêu cầu
    return {
      status: 0,
      data: null,
      message: error.message || "Lỗi không xác định",
    };
  }
};

/**
 * Client API để thực hiện các yêu cầu HTTP
 */
export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  // Quan trọng: Cho phép gửi cookie trong các yêu cầu cross-domain
  withCredentials: true,
});

/**
 * Thực hiện yêu cầu GET
 * @param endpoint - Endpoint API
 * @param config - Cấu hình tùy chọn Axios
 * @returns Promise chứa dữ liệu phản hồi
 */
export const get = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient.get(endpoint, config);
    return response.data;
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};

/**
 * Thực hiện yêu cầu POST
 * @param endpoint - Endpoint API
 * @param data - Dữ liệu gửi trong body
 * @param config - Cấu hình tùy chọn Axios
 * @returns Promise chứa dữ liệu phản hồi
 */
export const post = async <T>(
  endpoint: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient.post(
      endpoint,
      data,
      config
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};

/**
 * Thực hiện yêu cầu PUT
 * @param endpoint - Endpoint API
 * @param data - Dữ liệu gửi trong body
 * @param config - Cấu hình tùy chọn Axios
 * @returns Promise chứa dữ liệu phản hồi
 */
export const put = async <T>(
  endpoint: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient.put(
      endpoint,
      data,
      config
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};

/**
 * Thực hiện yêu cầu PATCH
 * @param endpoint - Endpoint API
 * @param data - Dữ liệu gửi trong body
 * @param config - Cấu hình tùy chọn Axios
 * @returns Promise chứa dữ liệu phản hồi
 */
export const patch = async <T>(
  endpoint: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient.patch(
      endpoint,
      data,
      config
    );
    return response.data;
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};

/**
 * Thực hiện yêu cầu DELETE
 * @param endpoint - Endpoint API
 * @param config - Cấu hình tùy chọn Axios
 * @returns Promise chứa dữ liệu phản hồi
 */
export const del = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient.delete(endpoint, config);
    return response.data;
  } catch (error) {
    throw handleApiError(error as AxiosError);
  }
};
