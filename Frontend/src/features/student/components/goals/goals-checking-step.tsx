"use client";

import React from "react";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";

export function GoalsCheckingStep() {
  return (
    <StudentLoadingState
      message="Đang phân tích cấu hình tài khoản học sinh..."
      messageClassName="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono"
      animated
      motionKey="checking"
    />
  );
}
