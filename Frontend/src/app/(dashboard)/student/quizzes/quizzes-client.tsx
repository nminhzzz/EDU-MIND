"use client";

import React, { useState, useEffect } from "react";
import { BrainCircuit, Trophy } from "lucide-react";
import { QuizHistoryTable } from "@/components/student/quiz-history-table";
import { GenerateQuizModal } from "@/components/student/generate-quiz-modal";
import { apiClient } from "@/services/api-client";

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

interface QuizzesClientProps {
  initialAttempts: Attempt[];
  initialSubjects: Subject[];
}

export function QuizzesClient({ initialAttempts, initialSubjects }: QuizzesClientProps) {
  const [attempts, setAttempts] = useState<Attempt[]>(initialAttempts);
  const [subjects, setSubjects] = useState<Subject[]>(initialSubjects);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  useEffect(() => {
    const fetchLatestData = async () => {
      try {
        if (subjects.length === 0) {
          const resSub = await apiClient.get<Subject[]>("/subjects/");
          setSubjects(resSub.data);
        }
      } catch (err) {
        console.error("Lỗi tải danh sách môn học phía Client:", err);
      }

      try {
        if (attempts.length === 0) {
          const resHist = await apiClient.get<Attempt[]>("/quizzes/student/history");
          setAttempts(resHist.data);
        }
      } catch (err) {
        console.error("Lỗi tải lịch sử bài tập phía Client:", err);
      }
    };

    fetchLatestData();
  }, []);

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
