"use client";

import React from "react";
import { motion } from "framer-motion";
import type { DraftResponse, Subject } from "@/features/student/types";
import { DraftPlanPreview } from "./draft-plan-preview";

interface GoalsDraftStepProps {
  draft: DraftResponse;
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
  loading: boolean;
  onConfirm: () => void;
  onCancelDraft: () => void;
  onUpdatePlan: (updatedPlan: DraftResponse["plan"]) => void;
}

export function GoalsDraftStep({
  draft,
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
  loading,
  onConfirm,
  onCancelDraft,
  onUpdatePlan,
}: GoalsDraftStepProps) {
  return (
    <motion.div
      key="roadmap_draft"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="grid grid-cols-1 lg:grid-cols-3 gap-6"
    >
      <div className="lg:col-span-2 space-y-5">
        <DraftPlanPreview
          draft={draft}
          subjects={subjects}
          selectedSubjectId={selectedSubjectId}
          targetScore={targetScore}
          deadline={deadline}
          onUpdatePlan={onUpdatePlan}
        />
      </div>

      <div className="space-y-5">
        <div className="bg-zinc-950 dark:bg-zinc-900 border border-zinc-850 p-6 rounded-2xl text-zinc-50 shadow-md">
          <span className="text-[10px] font-bold tracking-wider text-indigo-300 block uppercase">
            Hướng dẫn chỉnh sửa
          </span>
          <h3 className="text-sm font-black uppercase mt-1">ĐIỀU CHỈNH LỘ TRÌNH</h3>
          <p className="text-[11px] text-zinc-400 mt-3 leading-relaxed">
            Bạn có thể chỉnh sửa trực tiếp lộ trình bằng tay trên giao diện bên trái:
          </p>
          <ul className="text-[10px] text-zinc-400 mt-2 space-y-1.5 list-disc list-inside leading-relaxed">
            <li>Bấm vào tên bài học hoặc mô tả để chỉnh sửa nội dung.</li>
            <li>Thay đổi trực tiếp thời gian học của từng buổi.</li>
            <li>Chỉnh sửa các nhiệm vụ tuần để tối ưu lộ trình của mình.</li>
          </ul>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
            Nhấp vào xác nhận để lưu chính thức lộ trình học tập này vào dữ liệu lớp học và bắt đầu lộ trình hàng ngày.
          </p>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs tracking-wider transition-all shadow-md shadow-emerald-500/10 cursor-pointer disabled:opacity-50"
          >
            {loading ? "ĐANG KÍCH HOẠT..." : "XÁC NHẬN & BẮT ĐẦU HỌC ✓"}
          </button>
          <button
            type="button"
            onClick={onCancelDraft}
            className="w-full py-2.5 border border-red-200 dark:border-red-950/40 hover:bg-red-50 dark:hover:bg-red-950/20 text-red-600 dark:text-red-400 font-bold rounded-xl text-xs transition-all cursor-pointer"
          >
            HỦY BẢN NHÁP & LÀM LẠI ✕
          </button>
        </div>
      </div>
    </motion.div>
  );
}
