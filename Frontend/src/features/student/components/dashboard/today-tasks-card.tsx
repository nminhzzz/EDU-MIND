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
    <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between transition-all">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-zinc-200 dark:border-zinc-800 mb-6">
          <h2 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-zinc-50">
            Nhiệm vụ học tập hôm nay
          </h2>
          <span className="text-xs font-mono font-bold text-zinc-400 bg-zinc-50 dark:bg-zinc-950 px-2.5 py-1 rounded-lg border border-zinc-200 dark:border-zinc-800">
            {todayLabel}
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs font-mono text-zinc-400 tracking-wider">
            Đang tải dữ liệu nhiệm vụ...
          </div>
        ) : tasks.length === 0 ? (
          <div className="py-12 text-center text-sm text-zinc-500 dark:text-zinc-400 tracking-wide space-y-4">
            <p>Hôm nay bạn không có lịch học hay nhiệm vụ nào.</p>
            <Link
              href={ROUTES.STUDENT_GOALS}
              className="inline-block px-5 py-2.5 bg-zinc-50 hover:bg-zinc-100 dark:bg-zinc-950 dark:hover:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 hover:border-zinc-950 dark:hover:border-zinc-100 text-zinc-650 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-white rounded-xl font-bold text-xs"
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
