"use client";

import React from "react";
import { CalendarDays } from "lucide-react";
import { ROUTES } from "@/features/student/constants";
import type { StudyPlan } from "@/features/student/types";
import { TaskListItem } from "@/features/student/components/dashboard/task-list-item";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui";

interface DailyTasksViewProps {
  tasks: StudyPlan[];
  loading: boolean;
  todayLabel: string;
}

export function DailyTasksView({ tasks, loading, todayLabel }: DailyTasksViewProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6 text-left">
      <PageHeader
        eyebrow="Không gian học tập"
        title="Nhiệm vụ hôm nay"
        description="Chọn nhiệm vụ để học tài liệu, luyện tập và nhận hỗ trợ từ gia sư AI."
        actions={<span className="inline-flex items-center gap-2 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm font-semibold text-zinc-600 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
          <CalendarDays className="w-4 h-4 text-indigo-500" />
          {todayLabel}
        </span>}
      />

      {loading ? (
        <div className="space-y-3">{[0, 1, 2].map((item) => <Skeleton key={item} className="h-24" />)}</div>
      ) : tasks.length === 0 ? (
        <EmptyState title="Hôm nay chưa có nhiệm vụ" description="Tạo một lộ trình học để AI sắp xếp nhiệm vụ phù hợp với lịch của bạn." />
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskListItem key={task.id} task={task} href={ROUTES.STUDENT_TASK(task.id)} />
          ))}
        </div>
      )}
    </div>
  );
}
