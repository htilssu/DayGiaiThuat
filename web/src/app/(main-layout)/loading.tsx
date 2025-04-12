"use client";

import { IconLoader2 } from "@tabler/icons-react";

/**
 * Component hiển thị trạng thái loading cho main layout
 *
 * @returns {JSX.Element} Component hiển thị animation loading
 */
export default function Loading() {
  return (
    <div className="h-screen w-full flex items-center justify-center">
      <div className="text-center">
        <IconLoader2 className="h-12 w-12 text-primary animate-spin mx-auto" />
        <h2 className="mt-4 text-xl font-medium text-foreground/80">
          Đang tải...
        </h2>
        <p className="mt-2 text-foreground/60">Vui lòng đợi trong giây lát</p>
      </div>
    </div>
  );
}
