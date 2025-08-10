"use client";

import { useAppDispatch, useAppSelector } from "@/lib/store";
import { loadingUser, setUser } from "@/lib/store/userStore";
import { ReactNode, useEffect } from "react";
import { userApi } from "../lib/api";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const dispatch = useAppDispatch();
  const userState = useAppSelector((state) => state.user);
  useEffect(() => {
    // Chỉ gọi API khi ứng dụng được khởi tạo lần đầu
    if (userState.isInitial) {
      dispatch(loadingUser());
      userApi
        .getUserByToken()
        .then((data) => {
          console.log("AuthContext - received user data:", data);
          dispatch(setUser(data));
        })
        .catch((error) => {
          console.error("Lỗi khi lấy thông tin người dùng:", error);
        });
    }
  }, [dispatch, userState.isInitial]);

  return <>{children}</>;
}
