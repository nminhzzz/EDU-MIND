"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, BrainCircuit } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/services/api-client";

interface Subject {
  id: number;
  name: string;
  code: string;
}

interface GenerateQuizModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjects: Subject[];
}

export function GenerateQuizModal({ isOpen, onClose, subjects }: GenerateQuizModalProps) {
  const [generating, setGenerating] = useState(false);
  const [formData, setFormData] = useState({
    subject_id: "",
    topic: "",
    difficulty: "medium",
    total_questions: 5,
  });

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.subject_id || !formData.topic.trim()) {
      toast.error("Vui lòng nhập đầy đủ thông tin bắt buộc.");
      return;
    }
    setGenerating(true);
    try {
      const payload = {
        subject_id: parseInt(formData.subject_id),
        topic: formData.topic.trim(),
        difficulty: formData.difficulty,
        total_questions: formData.total_questions,
      };
      const res = await apiClient.post("/quizzes/generate", payload);
      const generatedQuiz = res.data;
      toast.success("AI đã sinh đề thành công! Bắt đầu làm bài.");
      onClose();
      window.location.href = `/student/quizzes/${generatedQuiz.id}`;
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || "AI sinh đề thất bại.";
      toast.error(errMsg);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-45"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-lg p-8 text-left">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-black text-zinc-900 dark:text-white flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-indigo-650" />
                  Sinh đề luyện thi AI RAG
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-650 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleGenerateQuiz} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-550 dark:text-zinc-400 uppercase tracking-wider mb-2">Môn học luyện tập *</label>
                  <select
                    value={formData.subject_id}
                    onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  >
                    <option value="">-- Chọn môn học --</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">Chủ đề kiến thức cần củng cố *</label>
                  <input
                    type="text"
                    value={formData.topic}
                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                    placeholder="VD: Cấu trúc điều kiện IF/ELSE hoặc Giải tích hàm số"
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">Độ khó đề</label>
                    <select
                      value={formData.difficulty}
                      onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-855 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                    >
                      <option value="easy">Dễ (Easy)</option>
                      <option value="medium">Vừa (Medium)</option>
                      <option value="hard">Khó (Hard)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">Số lượng câu hỏi</label>
                    <select
                      value={formData.total_questions}
                      onChange={(e) => setFormData({ ...formData, total_questions: parseInt(e.target.value) })}
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
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
