"use client";

import { useEffect } from "react";

/**
 * Component khởi tạo theme trên phía client để ngăn lỗi hydration
 * Áp dụng theme từ localStorage vào document trước khi render đầy đủ
 *
 * @returns {null} Không render gì ra UI
 */
export default function ThemeInitializer(): null {
  // Script để thêm ngay vào <head> để áp dụng theme trước khi React render
  useEffect(() => {
    // Script chạy một lần khi component mount
    const themeInitScript = `
      (function() {
        try {
          // Lấy theme từ localStorage nếu có
          var savedTheme = localStorage.getItem('theme');
          
          // Nếu không có trong localStorage, kiểm tra system preference
          if (!savedTheme) {
            savedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches 
              ? 'dark' 
              : 'light';
          }
          
          // Áp dụng theme vào document
          document.documentElement.setAttribute('data-theme', savedTheme);
          document.documentElement.dataset.theme = savedTheme;
        } catch (e) {
          console.error('Lỗi khi khởi tạo theme:', e);
        }
      })();
    `;

    // Tạo script element và chèn vào head
    if (
      !document.getElementById("theme-init-script") &&
      typeof window !== "undefined"
    ) {
      const scriptEl = document.createElement("script");
      scriptEl.id = "theme-init-script";
      scriptEl.innerHTML = themeInitScript;
      document.head.appendChild(scriptEl);
    }
  }, []);

  // Component này không render gì cả
  return null;
}
