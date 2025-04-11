"use client";

import Script from "next/script";

/**
 * Component chứa các script được chèn vào <head>
 * Script trong component này sẽ chạy trước khi React hydrate trên phía client
 *
 * @returns {React.ReactElement} Script elements để chèn vào head
 */
export default function HeadScripts(): React.ReactElement {
  return (
    <>
      <Script
        id="theme-initializer-script"
        strategy="beforeInteractive"
        dangerouslySetInnerHTML={{
          __html: `
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
              } catch (e) {}
            })();
          `,
        }}
      />
    </>
  );
}
