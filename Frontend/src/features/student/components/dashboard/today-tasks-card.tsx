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
    <div className="lg:col-span-2 bg-sky-50/30 dark:bg-sky-950/20 border border-sky-200/70 dark:border-sky-900/40 p-6 rounded-md shadow-xs flex flex-col justify-between transition-all">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-sky-200/60 dark:border-sky-900/50 mb-6">
          <h2 className="font-bold text-sm tracking-wide text-sky-950 dark:text-white">
            Nhiệm vụ học tập hôm nay
          </h2>
          <span className="text-xs font-mono font-bold text-sky-700 dark:text-sky-300 bg-white dark:bg-sky-900/60 px-2.5 py-1 rounded-md border border-sky-200 dark:border-sky-800 shadow-xs">
            {todayLabel}
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs font-mono text-sky-600/70 dark:text-sky-400/70 tracking-wider">
            Đang tải dữ liệu nhiệm vụ...
          </div>
        ) : tasks.length === 0 ? (
          <div className="py-12 text-center text-sm text-sky-900/70 dark:text-sky-300/70 tracking-wide space-y-4">
            <p>Hôm nay bạn không có lịch học hay nhiệm vụ nào.</p>
            <Link
              href={ROUTES.STUDENT_GOALS}
              className="inline-block px-5 py-2.5 bg-white hover:bg-sky-50 dark:bg-sky-900 dark:hover:bg-sky-800 border border-sky-200 dark:border-sky-700 text-sky-900 dark:text-sky-100 rounded-md font-bold text-xs shadow-xs"
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

      <div className="pt-6 border-t border-sky-200/60 dark:border-sky-900/50 mt-6 flex justify-end">
        <Link
          href={ROUTES.STUDENT_TASKS}
          className="text-xs font-bold text-sky-700 dark:text-sky-300 hover:text-sky-950 dark:hover:text-white hover:underline tracking-wide"
        >
          Xem tất cả nhiệm vụ hôm nay →
        </Link>
      </div>
    </div>
  );
}
