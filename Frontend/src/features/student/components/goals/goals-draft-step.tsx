"use client";

import React from "react";
import { motion } from "framer-motion";
import { CheckCircle, RefreshCw, Sparkles, HelpCircle } from "lucide-react";
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
      {/* Top Guidance Toolbar */}
      <div className="bg-gradient-to-r from-violet-900 via-indigo-900 to-zinc-900 border border-violet-700/50 p-5 rounded-3xl text-white shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-3 rounded-2xl bg-white/10 text-violet-200 backdrop-blur-md border border-white/10 shrink-0">
            <Sparkles className="w-6 h-6 text-amber-300" />
          </div>
          <div>
            <h3 className="text-xs font-black uppercase tracking-wider text-white flex items-center gap-1.5">
              HƯỚNG DẪN CHỈNH SỬA & XÁC NHẬN LỘ TRÌNH
            </h3>
            <p className="text-xs text-violet-200/90 font-medium mt-0.5 leading-relaxed">
              Bạn có thể nhấp trực tiếp vào tên bài học, nội dung hoặc giờ học để tùy chỉnh theo lịch cá nhân trước khi kích hoạt.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={onCancelDraft}
            className="px-4 py-2.5 border border-white/20 hover:bg-white/10 text-red-300 font-bold rounded-2xl text-xs transition-all cursor-pointer flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> HỦY BẢN NHÁP
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={loading}
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-white font-black rounded-2xl text-xs tracking-wider transition-all shadow-lg shadow-emerald-500/30 cursor-pointer disabled:opacity-50 flex items-center gap-2"
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

      {/* Bottom Sticky Action Bar */}
      <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/80 dark:border-zinc-800 p-4 rounded-3xl shadow-xl flex items-center justify-between gap-4 sticky bottom-4 z-20">
        <span className="text-xs font-bold text-zinc-500 dark:text-zinc-400 flex items-center gap-1.5 hidden sm:flex">
          <HelpCircle className="w-4 h-4 text-violet-500" /> Nhấn xác nhận khi bạn đã hài lòng với thời khóa biểu.
        </span>

        <div className="flex items-center gap-2.5 ml-auto">
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
            className="px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white font-black rounded-2xl text-xs tracking-wider transition-all shadow-lg shadow-emerald-600/30 cursor-pointer disabled:opacity-50 flex items-center gap-2"
          >
            <CheckCircle className="w-4.5 h-4.5" />
            {loading ? "ĐANG KÍCH HOẠT..." : "XÁC NHẬN & BẮT ĐẦU HỌC ✓"}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
