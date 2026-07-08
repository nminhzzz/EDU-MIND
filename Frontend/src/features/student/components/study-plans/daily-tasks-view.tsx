"use client";

import React from "react";
import Link from "next/link";
import { CalendarDays, Sparkles } from "lucide-react";
import { ROUTES } from "@/features/student/constants";
import type { StudyPlan } from "@/features/student/types";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";
import { TaskListItem } from "@/features/student/components/dashboard/task-list-item";

interface DailyTasksViewProps {
  tasks: StudyPlan[];
  loading: boolean;
  todayLabel: string;
}

export function DailyTasksView({ tasks, loading, todayLabel }: DailyTasksViewProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6 text-left">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-br from-white to-indigo-50/30 dark:from-zinc-900 dark:to-indigo-950/20 border border-zinc-200/80 dark:border-zinc-800 p-6 sm:p-8 rounded-2xl shadow-sm">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
              Nhiệm vụ học tập hôm nay
            </h1>
            <Sparkles className="w-5 h-5 text-indigo-500" />
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Chọn nhiệm vụ để vào không gian học tập với gia sư AI và bài kiểm tra nhanh.
          </p>
        </div>
        <span className="inline-flex items-center gap-2 self-start md:self-center text-xs font-mono font-bold text-zinc-500 dark:text-zinc-400 bg-white/80 dark:bg-zinc-950/60 px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800">
          <CalendarDays className="w-4 h-4 text-indigo-500" />
          {todayLabel}
        </span>
      </div>

      {loading ? (
        <StudentLoadingState
          message="Đang tải danh sách nhiệm vụ hôm nay..."
          messageClassName="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono"
        />
      ) : tasks.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-12 rounded-2xl text-center shadow-sm space-y-4">
          <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mx-auto">
            <CalendarDays className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-250">
              Hôm nay chưa có nhiệm vụ
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-md mx-auto leading-relaxed">
              Hãy tạo lộ trình học tập để AI sinh nhiệm vụ hàng ngày cho bạn.
            </p>
          </div>
          <Link
            href={ROUTES.STUDENT_GOALS}
            className="inline-flex px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all"
          >
            Tạo lộ trình học
          </Link>
        </div>
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
