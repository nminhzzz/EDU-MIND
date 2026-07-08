"use client";

import React from "react";
import { BrainCircuit } from "lucide-react";
import type { Subject } from "@/features/student/types";
import { StudentModal } from "@/features/student/components/common/student-modal";
import { useGenerateQuiz } from "@/features/student/hooks/use-generate-quiz";

interface GenerateQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjects: Subject[];
}

export function GenerateQuizModal({ isOpen, onClose, subjects }: GenerateQuizModalProps) {
  const { formData, generating, updateForm, handleGenerateQuiz } = useGenerateQuiz(onClose);

  return (
    <StudentModal
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="lg"
      title={
        <h2 className="text-xl font-black text-zinc-900 dark:text-white flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-indigo-650" />
          Sinh đề luyện thi AI RAG
        </h2>
      }
    >
      <form onSubmit={handleGenerateQuiz} className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-zinc-550 dark:text-zinc-400 uppercase tracking-wider mb-2">
            Môn học luyện tập *
          </label>
          <select
            value={formData.subject_id}
            onChange={(e) => updateForm({ subject_id: e.target.value })}
            className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          >
            <option value="">-- Chọn môn học --</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">
            Chủ đề kiến thức cần củng cố *
          </label>
          <input
            type="text"
            value={formData.topic}
            onChange={(e) => updateForm({ topic: e.target.value })}
            placeholder="VD: Cấu trúc điều kiện IF/ELSE hoặc Giải tích hàm số"
            className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">
              Độ khó đề
            </label>
            <select
              value={formData.difficulty}
              onChange={(e) => updateForm({ difficulty: e.target.value })}
              className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-855 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
            >
              <option value="easy">Dễ (Easy)</option>
              <option value="medium">Vừa (Medium)</option>
              <option value="hard">Khó (Hard)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">
              Số lượng câu hỏi
            </label>
            <select
              value={formData.total_questions}
              onChange={(e) => updateForm({ total_questions: parseInt(e.target.value, 10) })}
              className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-855 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
            >
              <option value={3}>3 câu</option>
              <option value={5}>5 câu</option>
              <option value={10}>10 câu</option>
            </select>
          </div>
        </div>
        <button
          type="submit"
          disabled={generating}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer"
        >
          {generating ? "AI đang lập luận đề thi..." : "Bắt đầu sinh đề luyện thi"}
        </button>
      </form>
    </StudentModal>
  );
}
