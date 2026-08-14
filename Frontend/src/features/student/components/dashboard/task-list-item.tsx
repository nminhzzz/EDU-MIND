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
          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all select-none shrink-0 ${isDone
              ? "bg-sky-600 border-sky-600 text-white"
              : "border-sky-300 dark:border-sky-700 bg-white dark:bg-sky-950/40"
            }`}
        >
          {isDone && <span className="text-[10px] font-black">✓</span>}
        </div>
        <div className="min-w-0">
          <p
            className={`text-sm font-bold text-sky-950 dark:text-sky-100 truncate ${isDone ? "line-through text-sky-900/40 dark:text-sky-300/40" : ""}`}
          >
            {task.title}
          </p>
          <p className="text-[10px] text-sky-900/60 dark:text-sky-300/60 mt-0.5 font-medium">
            Lịch học: {task.start_time.substring(0, 5)} - {task.end_time.substring(0, 5)}
          </p>
        </div>
      </div>

      <span
        className={`shrink-0 text-[10px] font-bold px-3 py-1 border rounded-full ${isDone
            ? "bg-sky-50 dark:bg-sky-900/50 border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-300"
            : task.status === "doing"
              ? "bg-sky-500 border-sky-600 text-white font-bold shadow-xs"
              : "bg-sky-50/50 dark:bg-slate-900 border-sky-200/60 dark:border-slate-800 text-sky-800/60 dark:text-slate-400"
          }`}
      >
        {isDone ? "Đã xong" : task.status === "doing" ? "Đang làm" : "Chưa làm"}
      </span>
    </>
  );
}

const itemClassName = (isDone: boolean) =>
  `flex items-center justify-between gap-4 p-4 border rounded-xl transition-all cursor-pointer ${isDone
    ? "border-sky-100 dark:border-sky-900/30 bg-sky-50/30 dark:bg-sky-950/20 opacity-60"
    : "border-sky-200/80 dark:border-sky-900/50 hover:border-sky-400 dark:hover:border-sky-700 bg-white dark:bg-sky-950/40 hover:shadow-xs"
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
