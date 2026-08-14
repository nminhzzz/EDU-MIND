"use client";

import { useEffect } from "react";
import { ErrorState } from "@/components/ui";

export default function DashboardError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error("Dashboard render error", error);
  }, [error]);

  return (
    <div className="mx-auto w-full max-w-2xl py-12">
      <ErrorState
        title="Không thể hiển thị nội dung"
        description="Đã có lỗi khi tải màn hình này. Dữ liệu của bạn vẫn an toàn, hãy thử tải lại."
        onAction={reset}
      />
    </div>
  );
}
