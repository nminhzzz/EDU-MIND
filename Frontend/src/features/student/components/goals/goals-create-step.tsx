"use client";

import React from "react";
import { motion } from "framer-motion";
import type { Subject } from "@/features/student/types";

interface GoalsCreateStepProps {
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
  loading: boolean;
  onSubjectChange: (value: string) => void;
  onTargetScoreChange: (value: number) => void;
  onDeadlineChange: (value: string) => void;
  onScheduleEditClick: () => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function GoalsCreateStep({
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
  loading,
  onSubjectChange,
  onTargetScoreChange,
  onDeadlineChange,
  onScheduleEditClick,
  onSubmit,
}: GoalsCreateStepProps) {
  return (
    <motion.div
      key="create_goal"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm">
        <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase mb-6">
          THIẾT LẬP MỤC TIÊU HỌC TẬP MỚI
        </h2>

        <form onSubmit={onSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
              Chọn môn học cần lên lộ trình:
            </label>
            <select
              value={selectedSubjectId}
              onChange={(e) => onSubjectChange(e.target.value)}
              className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
            >
              {subjects.length === 0 ? (
                <option value="">Không tìm thấy môn học nào</option>
              ) : (
                subjects.map((sub) => (
                  <option key={sub.id} value={sub.id}>
                    {sub.name} ({sub.code})
                  </option>
                ))
              )}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-2">
              <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                Điểm số mục tiêu mong muốn (1 - 10):
              </label>
              <input
                type="number"
                min={1}
                max={10}
                step={0.5}
                value={targetScore}
                onChange={(e) => onTargetScoreChange(Number(e.target.value))}
                className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                Hạn chót phải hoàn thành (Deadline):
              </label>
              <input
                type="date"
                min={new Date().toISOString().split("T")[0]}
                value={deadline}
                onChange={(e) => onDeadlineChange(e.target.value)}
                className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
              />
            </div>
          </div>

          <div className="pt-4 flex flex-col md:flex-row items-center justify-between gap-4">
            <button
              type="button"
              onClick={onScheduleEditClick}
              className="text-xs font-bold text-zinc-500 hover:text-zinc-950 dark:hover:text-white hover:underline cursor-pointer"
            >
              Thay đổi lịch học / cấu hình thời gian rảnh
            </button>

            <button
              type="submit"
              disabled={loading}
              className="w-full md:w-fit px-8 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer disabled:opacity-50 shadow-md shadow-indigo-500/10"
            >
              {loading ? "AI ĐANG LẬP LỘ TRÌNH..." : "AI LẬP LỘ TRÌNH THỬ NGAY ->"}
            </button>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
