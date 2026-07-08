"use client";

import React from "react";
import Link from "next/link";
import { AlertCircle } from "lucide-react";
import type { StudyPlan } from "@/features/student/types";

interface TaskStudyFooterProps {
  task: StudyPlan;
  backHref?: string;
  onClose?: () => void;
}

export function TaskStudyFooter({ task, backHref, onClose }: TaskStudyFooterProps) {
  return (
    <div className="p-4 border-t border-zinc-150 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/10 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
      <span className="text-[10px] text-zinc-400 font-bold dark:text-zinc-500">
        Lịch học: {task.start_time.substring(0, 5)} - {task.end_time.substring(0, 5)}
      </span>
      <div className="flex flex-wrap items-center gap-3">
        {backHref ? (
          <Link
            href={backHref}
            className="px-4 py-2 border border-zinc-200 dark:border-zinc-750 text-xs font-bold rounded-xl text-zinc-500 hover:text-zinc-800 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
          >
            Quay lại danh sách
          </Link>
        ) : (
          onClose && (
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-zinc-200 dark:border-zinc-750 text-xs font-bold rounded-xl text-zinc-500 hover:text-zinc-800 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer"
            >
              Đóng lại
            </button>
          )
        )}
        {task.status !== "done" && (
          <div className="flex items-center gap-1.5 px-4 py-2 bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 rounded-xl text-xs font-bold">
            <AlertCircle className="w-4 h-4 shrink-0" />
            Cần đạt ≥ 8 điểm Quick Quiz để hoàn thành
          </div>
        )}
      </div>
    </div>
  );
}
