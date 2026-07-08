"use client";

import React from "react";
import Link from "next/link";
import { BookOpen, ChevronLeft } from "lucide-react";

interface TaskStudyHeaderProps {
  title: string;
  backHref?: string;
  onClose?: () => void;
}

export function TaskStudyHeader({ title, backHref, onClose }: TaskStudyHeaderProps) {
  return (
    <div className="p-5 border-b border-zinc-150 dark:border-zinc-800 flex justify-between items-center bg-zinc-50/50 dark:bg-zinc-900/10 gap-4">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
          <BookOpen className="w-5 h-5" />
        </div>
        <div className="text-left min-w-0">
          <span className="text-[9px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block font-mono">
            Không gian học tập nhiệm vụ hàng ngày
          </span>
          <h3 className="text-sm sm:text-base font-extrabold text-zinc-800 dark:text-zinc-100 truncate">
            {title}
          </h3>
        </div>
      </div>

      {backHref ? (
        <Link
          href={backHref}
          className="inline-flex items-center gap-1.5 shrink-0 px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-700 text-xs font-bold text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Danh sách
        </Link>
      ) : (
        onClose && (
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer shrink-0"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        )
      )}
    </div>
  );
}
