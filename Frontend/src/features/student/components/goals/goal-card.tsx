"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Calendar, Target, Trash2 } from "lucide-react";
import { ROUTES } from "@/features/student/constants";
import type { StudyGoalResponse, Subject } from "@/features/student/types";

interface GoalCardProps {
  goal: StudyGoalResponse;
  subject?: Subject;
  goalsLoading: boolean;
  onDelete: (id: number) => void;
}

function getStatusStyle(status: string) {
  switch (status) {
    case "active":
      return {
        label: "Đang chạy",
        className:
          "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800",
      };
    case "completed":
      return {
        label: "Đã hoàn thành",
        className:
          "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-800",
      };
    case "cancelled":
      return {
        label: "Đã hủy",
        className:
          "bg-zinc-100 text-zinc-600 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
      };
    default:
      return {
        label: status,
        className:
          "bg-zinc-100 text-zinc-600 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
      };
  }
}

export function GoalCard({ goal, subject, goalsLoading, onDelete }: GoalCardProps) {
  const status = getStatusStyle(goal.status);

  return (
    <article className="group h-full flex flex-col rounded-2xl border border-zinc-200/90 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md hover:border-indigo-300/80 dark:hover:border-indigo-700/60 transition-all duration-200 overflow-hidden">
      <div className="p-5 sm:p-6 flex-1 flex flex-col">
        <div className="flex items-center justify-between gap-3 mb-3">
          <span className="inline-flex items-center text-[10px] font-extrabold tracking-wide text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-100 dark:border-indigo-900 px-2.5 py-1 rounded-lg uppercase">
            {subject?.code || "MÔN HỌC"}
          </span>
          <span
            className={`inline-flex items-center shrink-0 text-[10px] font-bold px-2.5 py-1 rounded-lg border whitespace-nowrap ${status.className}`}
          >
            {status.label}
          </span>
        </div>

        <Link href={ROUTES.STUDENT_GOAL_DETAIL(goal.id)} className="block group-hover:text-indigo-600 transition-colors">
          <h3 className="text-[15px] sm:text-base font-extrabold text-zinc-900 dark:text-zinc-100 leading-snug line-clamp-2 min-h-[2.75rem]">
            {goal.title || `Lộ trình môn ${subject?.name || ""}`}
          </h3>
        </Link>

        {subject?.name && (
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 truncate">{subject.name}</p>
        )}

        <div className="mt-5 grid grid-cols-2 gap-3 p-3.5 rounded-xl bg-zinc-50/90 dark:bg-zinc-950/40 border border-zinc-100 dark:border-zinc-800/80">
          <div className="space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 flex items-center gap-1">
              <Target className="w-3 h-3" />
              Mục tiêu điểm
            </p>
            <p className="text-sm font-black text-zinc-900 dark:text-zinc-100">
              {goal.target_score.toFixed(1)}
              <span className="text-zinc-400 font-semibold"> / 10</span>
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              Ngày hoàn thành
            </p>
            <p className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
              {new Date(goal.deadline).toLocaleDateString("vi-VN")}
            </p>
          </div>
        </div>
      </div>

      <div className="px-5 sm:px-6 py-4 border-t border-zinc-100 dark:border-zinc-800/90 bg-zinc-50/40 dark:bg-zinc-900/40 flex items-center justify-between gap-3">
        <Link
          href={ROUTES.STUDENT_GOAL_DETAIL(goal.id)}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-sm shadow-indigo-500/20 transition-all active:scale-[0.98]"
        >
          Xem chi tiết lộ trình
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
        <button
          type="button"
          onClick={() => onDelete(goal.id)}
          disabled={goalsLoading}
          className="p-2.5 text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 border border-transparent hover:border-red-100 dark:hover:border-red-900/40 rounded-xl transition-colors cursor-pointer disabled:opacity-50"
          title="Xóa lộ trình học"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </article>
  );
}
