"use client";

import React from "react";
import Link from "next/link";
import { ROUTES } from "@/features/student/constants";
import type { StudyPlan } from "@/features/student/types";
import { TaskListItem } from "./task-list-item";

interface TodayTasksCardProps {
  tasks: StudyPlan[];
  loading: boolean;
  todayLabel: string;
}

export function TodayTasksCard({ tasks, loading, todayLabel }: TodayTasksCardProps) {
  return (
    <div className="lg:col-span-2 bg-card border border-border p-6 rounded-xl shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-border mb-6">
          <h2 className="font-semibold text-sm text-foreground">
            Nhiệm vụ học tập hôm nay
          </h2>
          <span className="text-xs font-mono font-medium text-muted-foreground bg-muted px-2.5 py-1 rounded-md border border-border">
            {todayLabel}
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs font-mono text-muted-foreground">
            Đang tải dữ liệu nhiệm vụ...
          </div>
        ) : tasks.length === 0 ? (
          <div className="py-12 text-center text-sm text-muted-foreground space-y-4">
            <p>Hôm nay bạn không có lịch học hay nhiệm vụ nào.</p>
            <Link
              href={ROUTES.STUDENT_GOALS}
              className="inline-block px-5 py-2.5 bg-background hover:bg-accent border border-input text-foreground rounded-lg font-medium text-xs transition-colors"
            >
              Tạo lộ trình ngay
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.slice(0, 4).map((task) => (
              <TaskListItem key={task.id} task={task} href={ROUTES.STUDENT_TASK(task.id)} />
            ))}
          </div>
        )}
      </div>

      <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800 mt-6 flex justify-end">
        <Link
          href={ROUTES.STUDENT_TASKS}
          className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline tracking-wide"
        >
          Xem tất cả nhiệm vụ hôm nay →
        </Link>
      </div>
    </div>
  );
}
