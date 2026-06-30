"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, BookOpen, MessageSquare, GraduationCap, CheckCircle, AlertCircle } from "lucide-react";
import { TutorMiniChat } from "./tutor-mini-chat";
import { QuickQuizPane } from "./quick-quiz-pane";
import { MarkdownText } from "./markdown-text";

interface TaskStudyModalProps {
  task: {
    id: number;
    title: string;
    task_description?: string;
    rag_content?: string;
    subject_id?: number;
    status: string;
    start_time: string;
    end_time: string;
  };
  onClose: () => void;
  onToggleStatus: (task: any) => Promise<void>;
  onRefresh?: () => void;
}

export function TaskStudyModal({ task, onClose, onToggleStatus, onRefresh }: TaskStudyModalProps) {
  const [activeTab, setActiveTab] = useState<"material" | "quiz">("material");
  const [submitting, setSubmitting] = useState(false);
  const [quizSuccess, setQuizSuccess] = useState(false);

  const subjectId = task.subject_id || 1; // Fallback to 1 if not available

  const handleMarkDone = async () => {
    setSubmitting(true);
    try {
      await onToggleStatus(task);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* Overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 bg-black z-40"
      />

      {/* Modal Container */}
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 15 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="p-5 border-b border-zinc-150 dark:border-zinc-800 flex justify-between items-center bg-zinc-50/50 dark:bg-zinc-900/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                <BookOpen className="w-5 h-5" />
              </div>
              <div className="text-left">
                <span className="text-[9px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block font-mono">
                  Không gian học tập nhiệm vụ hàng ngày
                </span>
                <h3 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-100 max-w-xl truncate">
                  {task.title}
                </h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
            {/* Cột trái: Tài liệu & Trắc nghiệm */}
            <div className="border-r border-zinc-200 dark:border-zinc-800 flex flex-col h-full overflow-hidden">
              {/* Tab selector */}
              <div className="flex border-b border-zinc-200 dark:border-zinc-800">
                <button
                  onClick={() => setActiveTab("material")}
                  className={`flex-1 py-3 text-xs font-bold transition-all border-b-2 cursor-pointer ${
                    activeTab === "material"
                      ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                      : "border-transparent text-zinc-400 dark:text-zinc-500 hover:text-zinc-700"
                  }`}
                >
                  📖 Hướng dẫn học tập
                </button>
                <button
                  onClick={() => setActiveTab("quiz")}
                  className={`flex-1 py-3 text-xs font-bold transition-all border-b-2 cursor-pointer ${
                    activeTab === "quiz"
                      ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                      : "border-transparent text-zinc-400 dark:text-zinc-500 hover:text-zinc-700"
                  }`}
                >
                  📝 Kiểm tra trắc nghiệm nhanh
                </button>
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {activeTab === "material" ? (
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
                ) : (
                  <div className="h-full">
                    <QuickQuizPane
                      subjectId={subjectId}
                      topic={task.title}
                      studyPlanId={task.id}
                      onSuccess={() => {
                        setQuizSuccess(true);
                        if (onRefresh) onRefresh();
                      }}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Cột phải: Gia sư AI Chat */}
            <div className="flex flex-col h-full overflow-hidden p-6 space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-100 dark:border-zinc-800/80 text-left">
                <MessageSquare className="w-4.5 h-4.5 text-indigo-500" />
                <h4 className="text-xs font-extrabold text-zinc-850 dark:text-zinc-200 uppercase tracking-wide">
                  Gia sư AI 24/7
                </h4>
              </div>
              <div className="flex-1 overflow-hidden">
                <TutorMiniChat subjectId={subjectId} topic={task.title} />
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-zinc-150 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/10 flex justify-between items-center">
            <span className="text-[10px] text-zinc-400 font-bold dark:text-zinc-500">
              Lịch học: {task.start_time.substring(0, 5)} - {task.end_time.substring(0, 5)}
            </span>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-zinc-200 dark:border-zinc-750 text-xs font-bold rounded-xl text-zinc-500 hover:text-zinc-800 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 cursor-pointer"
              >
                Đóng lại
              </button>
              {task.status !== "done" && (
                <div className="flex items-center gap-1.5 px-4 py-2 bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 rounded-xl text-xs font-bold">
                  <AlertCircle className="w-4 h-4" />
                  Cần đạt ≥ 8 điểm Quick Quiz để hoàn thành
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </>
  );
}
