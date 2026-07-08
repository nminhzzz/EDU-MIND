"use client";

import React from "react";
import { AlertCircle } from "lucide-react";
import { StudentEmptyState } from "@/features/student/components/common/student-empty-state";

export function RecommendationsEmptyState() {
  return (
    <StudentEmptyState
      icon={AlertCircle}
      title="Chưa có đề xuất ôn tập nào"
      description="Đề xuất ôn tập từ AI sẽ được tự động tạo khi bạn làm bài thi thử đạt kết quả dưới 8.0 điểm. Hãy tiếp tục cố gắng trong các bài kiểm tra nhé!"
      animated
      motionKey="empty"
    />
  );
}
