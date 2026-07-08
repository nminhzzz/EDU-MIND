"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ROUTES } from "@/features/student/constants";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";
import { TaskStudyView } from "@/features/student/components/study-plans/task-study-view";
import { useTaskDetail } from "@/features/student/hooks/use-task-detail";

export default function StudentTaskDetailPage() {
  const params = useParams();
  const taskId = params?.id as string | undefined;
  const { task, loading, refreshTask } = useTaskDetail(taskId);

  if (loading || !task) {
    return (
      <StudentLoadingState
        message="Đang mở không gian học tập nhiệm vụ..."
        messageClassName="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono"
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-2 px-1 sm:px-2">
      <TaskStudyView task={task} backHref={ROUTES.STUDENT_TASKS} onRefresh={refreshTask} />
    </div>
  );
}
