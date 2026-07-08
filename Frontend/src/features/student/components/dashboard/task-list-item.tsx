"use client";

import React from "react";
import Link from "next/link";
import type { StudyPlan } from "@/features/student/types";

interface TaskListItemProps {
  task: StudyPlan;
  href?: string;
  onClick?: (task: StudyPlan) => void;
}

function TaskListItemContent({ task }: { task: StudyPlan }) {
  const isDone = task.status === "done";

  return (
    <>
      <div className="flex items-center gap-4 min-w-0">
        <div
          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all select-none shrink-0 ${
            isDone
              ? "bg-indigo-600 border-indigo-600 text-white"
              : "border-zinc-300 dark:border-zinc-750 bg-white dark:bg-zinc-900"
          }`}
        >
          {isDone && <span className="text-[10px] font-black">✓</span>}
        </div>
        <div className="min-w-0">
          <p
            className={`text-sm font-bold text-zinc-800 dark:text-zinc-200 truncate ${isDone ? "line-through text-zinc-400 dark:text-zinc-500" : ""}`}
          >
            {task.title}
          </p>
          <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
            Lịch học: {task.start_time.substring(0, 5)} - {task.end_time.substring(0, 5)}
          </p>
        </div>
      </div>

      <span
        className={`shrink-0 text-[10px] font-bold px-3 py-1 border rounded-full ${
          isDone
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
            : task.status === "doing"
              ? "bg-indigo-50/10 border-indigo-50/20 text-indigo-600 dark:text-indigo-400 animate-pulse"
              : "bg-zinc-50 dark:bg-zinc-950 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500"
        }`}
      >
        {isDone ? "Đã xong" : task.status === "doing" ? "Đang làm" : "Chưa làm"}
      </span>
    </>
  );
}

const itemClassName = (isDone: boolean) =>
  `flex items-center justify-between gap-4 p-4 border rounded-xl transition-all cursor-pointer ${
    isDone
      ? "border-zinc-100 dark:border-zinc-850 bg-zinc-50/50 dark:bg-zinc-950/20 opacity-60"
      : "border-zinc-200 dark:border-zinc-800 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-zinc-900 hover:shadow-sm"
  }`;

export function TaskListItem({ task, href, onClick }: TaskListItemProps) {
  const isDone = task.status === "done";

  if (href) {
    return (
      <Link href={href} className={itemClassName(isDone)}>
        <TaskListItemContent task={task} />
      </Link>
    );
  }

  return (
    <div
      onClick={() => onClick?.(task)}
      className={itemClassName(isDone)}
      role={onClick ? "button" : undefined}
    >
      <TaskListItemContent task={task} />
    </div>
  );
}
