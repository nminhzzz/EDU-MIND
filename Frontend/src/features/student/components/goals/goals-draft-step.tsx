"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle, RefreshCw, Edit3 } from "lucide-react";
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
      className="space-y-6 max-w-5xl mx-auto w-full"
    >
      {/* Top Banner Action Toolbar */}
      <div className="bg-zinc-950 dark:bg-zinc-900 border border-zinc-800 p-5 rounded-3xl text-zinc-50 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shrink-0">
            <Edit3 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xs font-black uppercase tracking-wider text-white">
              HƯỚNG DẪN CHỈNH SỬA THỜI KHÓA BIỂU
            </h3>
            <p className="text-[11px] text-zinc-400 font-medium mt-0.5">
              Mỗi ngày hiển thị trên 1 hàng riêng biệt. Nhấp trực tiếp vào Tên bài học, Mô tả, Ngày tháng hoặc Giờ học để điều chỉnh.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={onCancelDraft}
            className="px-4 py-3 border border-zinc-800 hover:bg-zinc-800 text-red-400 font-bold rounded-2xl text-xs transition-all cursor-pointer flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> HỦY BẢN NHÁP
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-2xl text-xs tracking-wider transition-all shadow-lg shadow-emerald-500/20 cursor-pointer disabled:opacity-50 flex items-center gap-2"
          >
            <CheckCircle className="w-4 h-4" />
            {loading ? "ĐANG KÍCH HOẠT..." : "XÁC NHẬN & BẮT ĐẦU HỌC ✓"}
          </button>
        </div>
      </div>

      {/* Main Full-Width Plan Preview */}
      <DraftPlanPreview
        draft={draft}
        subjects={subjects}
        selectedSubjectId={selectedSubjectId}
        targetScore={targetScore}
        deadline={deadline}
        onUpdatePlan={onUpdatePlan}
      />

      {/* Bottom Sticky Action Bar for Easy Scrolling Access */}
      <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-md border border-zinc-200/80 dark:border-zinc-800 p-4 rounded-3xl shadow-lg flex items-center justify-between gap-4 sticky bottom-4 z-20">
        <span className="text-xs font-bold text-zinc-500 dark:text-zinc-400">
          💡 Nhấn nút bên phải khi bạn đã hoàn tất chỉnh sửa thời khóa biểu.
        </span>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onCancelDraft}
            className="px-4 py-3 border border-red-200 dark:border-red-950/40 hover:bg-red-50 dark:hover:bg-red-950/20 text-red-600 dark:text-red-400 font-bold rounded-2xl text-xs transition-all cursor-pointer flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> HỦY BẢN NHÁP
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-black rounded-2xl text-xs tracking-wider transition-all shadow-lg shadow-emerald-500/20 cursor-pointer disabled:opacity-50 flex items-center gap-2"
          >
            <CheckCircle className="w-4 h-4" />
            {loading ? "ĐANG KÍCH HOẠT..." : "XÁC NHẬN & BẮT ĐẦU HỌC ✓"}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
