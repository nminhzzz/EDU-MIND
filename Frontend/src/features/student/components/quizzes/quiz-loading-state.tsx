"use client";

import React from "react";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";

export function QuizLoadingState() {
  return (
    <StudentLoadingState
      message="Đang đồng bộ dữ liệu bài thi..."
      messageClassName="text-sm font-medium text-zinc-500"
    />
  );
}
