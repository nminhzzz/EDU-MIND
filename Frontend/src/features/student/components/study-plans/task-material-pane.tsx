"use client";

import React from "react";
import { GraduationCap } from "lucide-react";
import { MarkdownText } from "@/components/student/markdown-text";
import type { StudyPlan } from "@/features/student/types";

interface TaskMaterialPaneProps {
  task: StudyPlan;
}

export function TaskMaterialPane({ task }: TaskMaterialPaneProps) {
  return (
    <div className="space-y-5 text-left">
      <div className="bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/50 dark:border-zinc-850 p-4 rounded-xl">
        <h4 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200 mb-2">
          📋 Chi tiết nhiệm vụ hôm nay
        </h4>
        <p className="text-xs text-zinc-650 dark:text-zinc-400 leading-relaxed font-semibold">
          {task.task_description || "Nghiên cứu chủ đề bài học của ngày hôm nay."}
        </p>
      </div>

      {task.rag_content ? (
        <div className="bg-indigo-50/15 dark:bg-indigo-950/10 border border-indigo-100 dark:border-indigo-900/60 p-4 rounded-xl space-y-2.5 shadow-sm">
          <h4 className="text-xs font-extrabold text-indigo-650 dark:text-indigo-400 flex items-center gap-1.5">
            📚 Tài liệu học tập tự động (RAG)
          </h4>
          <MarkdownText
            content={task.rag_content}
            className="text-xs text-zinc-650 dark:text-zinc-300 leading-relaxed font-medium"
          />
        </div>
      ) : (
        <div className="bg-zinc-50/50 dark:bg-zinc-950/10 border border-zinc-200/50 dark:border-zinc-800 p-4 rounded-xl space-y-2 text-center">
          <h4 className="text-xs font-extrabold text-indigo-650 dark:text-indigo-400">
            📚 Gia sư AI & Giáo trình tương tác
          </h4>
          <p className="text-[11px] text-zinc-500 dark:text-zinc-400 leading-relaxed font-semibold">
            Hãy sử dụng khung chat <strong>Gia sư AI 24/7</strong> ở phía bên phải để yêu cầu tóm tắt lý thuyết, giải thích định nghĩa hoặc lấy ví dụ thực tế cho chủ đề này bất cứ lúc nào!
          </p>
        </div>
      )}

      <div className="border border-zinc-200/80 dark:border-zinc-800 rounded-xl p-4 space-y-3 bg-white dark:bg-zinc-900/50">
        <h4 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200 flex items-center gap-1.5">
          <GraduationCap className="w-4 h-4 text-indigo-500" />
          Gợi ý phương pháp học tập
        </h4>
        <ul className="text-[11px] text-zinc-500 space-y-2 list-disc pl-4 font-semibold leading-relaxed">
          <li>Đọc và phân tích kỹ các khái niệm cốt lõi của chủ đề.</li>
          <li>Sử dụng khung chat "Gia sư AI 24/7" bên phải nếu gặp bất kỳ định nghĩa hay ví dụ nào khó hiểu.</li>
          <li>Sau khi đã nắm vững lý thuyết, hãy chuyển sang tab "Kiểm tra trắc nghiệm nhanh" để tự đánh giá kiến thức của bản thân.</li>
        </ul>
      </div>
    </div>
  );
}
