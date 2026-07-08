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
  chatMessage: string;
  chatLoading: boolean;
  loading: boolean;
  onChatMessageChange: (value: string) => void;
  onSendMessage: (e: React.FormEvent) => void;
  onConfirm: () => void;
  onCancelDraft: () => void;
}

export function GoalsDraftStep({
  draft,
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
  chatMessage,
  chatLoading,
  loading,
  onChatMessageChange,
  onSendMessage,
  onConfirm,
  onCancelDraft,
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
        />
      </div>

      <div className="space-y-5">
        <div className="bg-zinc-950 dark:bg-zinc-900 border border-zinc-850 p-6 rounded-2xl text-zinc-50 shadow-md">
          <span className="text-[10px] font-bold tracking-wider text-indigo-300 block uppercase">
            Thảo luận với AI
          </span>
          <h3 className="text-sm font-black uppercase mt-1">ĐIỀU CHỈNH LỘ TRÌNH</h3>
          <p className="text-[10px] text-zinc-400 mt-2 leading-relaxed">
            Nếu bạn muốn thay đổi bất kỳ phần nào của lộ trình (ví dụ: chuyển bài học giữa các tuần, học thêm chủ đề cụ thể...), hãy yêu cầu AI ngay bên dưới.
          </p>

          <form onSubmit={onSendMessage} className="mt-5 space-y-3">
            <textarea
              rows={3}
              placeholder="Nhập yêu cầu điều chỉnh lộ trình..."
              value={chatMessage}
              onChange={(e) => onChatMessageChange(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-zinc-800 rounded-xl bg-zinc-900 text-white font-medium focus:outline-none focus:border-indigo-500 placeholder-zinc-500"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatMessage.trim()}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-850 text-white font-bold rounded-xl text-xs transition-all cursor-pointer"
            >
              {chatLoading ? "AI ĐANG ĐIỀU CHỈNH..." : "GỬI YÊU CẦU ĐỔI ->"}
            </button>
          </form>
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
