"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { BrainCircuit, Trophy } from "lucide-react";
import { QuizHistoryTable } from "@/components/student/quiz-history-table";
import { GenerateQuizModal } from "@/components/student/generate-quiz-modal";

interface Subject {
  id: number;
  name: string;
  code: string;
}

interface Attempt {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
}

export default function StudentQuizzesPage() {
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  const fetchData = async () => {
    try {
      const [historyRes, subjRes] = await Promise.all([
        apiClient.get<Attempt[]>("/quizzes/student/history"),
        apiClient.get<Subject[]>("/subjects/"),
      ]);
      setAttempts(historyRes.data);
      setSubjects(subjRes.data);
    } catch (err) {
      console.error("Lỗi khi tải lịch sử luyện đề:", err);
      toast.error("Không thể tải lịch sử luyện đề.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-650 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Đang tải lịch sử bài làm...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-left">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white">Luyện Đề Thi & Bài Tập</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Tự ôn tập củng cố kiến thức bằng các đề trắc nghiệm tạo tự động từ AI RAG.
          </p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer flex items-center gap-2"
        >
          <BrainCircuit className="w-4 h-4" />
          Sinh đề thi bằng AI
        </button>
      </div>

      {/* Lịch sử làm bài */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="font-extrabold text-sm text-zinc-855 dark:text-zinc-250 flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
          <Trophy className="w-4 h-4 text-amber-500" />
          Lịch sử bài thi đã làm
        </h2>

        <QuizHistoryTable
          attempts={attempts}
          onGenerateClick={() => setShowGenerateModal(true)}
        />
      </div>

      {/* Modal sinh đề AI */}
      <GenerateQuizModal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        subjects={subjects}
      />
    </div>
  );
}
