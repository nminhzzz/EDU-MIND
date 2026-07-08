"use client";

import React from "react";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";

export function RecommendationsLoadingState() {
  return (
    <StudentLoadingState
      message="Đang tải danh sách đề xuất ôn tập AI..."
      messageClassName="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono"
      animated
      motionKey="loading"
    />
  );
}
