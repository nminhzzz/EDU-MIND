"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { CheckCircle2, AlertCircle, Clock, Trophy, ChevronRight, ChevronLeft, Send, RotateCcw } from "lucide-react";

interface Option {
  key: string;
  value: string;
}

interface Question {
  question_text: string;
  options: Option[];
  correct_answer?: string; // Chỉ có ở chế độ review
  explanation?: string;     // Chỉ có ở chế độ review
}

interface Quiz {
  id: number;
  title: string;
  difficulty: string;
  total_questions: number;
  questions: Question[];
}

export default function StudentQuizDetailPage() {
  const params = useParams();
  const router = useRouter();
  const quizId = params.id;

  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [isReview, setIsReview] = useState(false);
  const [attemptResult, setAttemptResult] = useState<any>(null);

  // Trạng thái làm bài
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [startTime, setStartTime] = useState<number>(0);
  const [duration, setDuration] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  // Timer interval
  useEffect(() => {
    if (loading || isReview) return;
    const interval = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [loading, isReview]);

  const loadQuiz = async () => {
    setLoading(true);
    try {
      // 1. Thử gọi API review xem học sinh đã làm bài chưa
      const reviewRes = await apiClient.get<Quiz>(`/quizzes/${quizId}/review`);
      setQuiz(reviewRes.data);
      setIsReview(true);
    } catch (err: any) {
      // 2. Chưa làm bài (403 Forbidden), tiến hành tải đề thi bình thường (ẩn đáp án)
      try {
        const quizRes = await apiClient.get<Quiz>(`/quizzes/${quizId}`);
        setQuiz(quizRes.data);
        setIsReview(false);
        setStartTime(Date.now());
      } catch (err2: any) {
        toast.error("Không thể tải thông tin đề thi.");
        router.push("/student/quizzes");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (quizId) {
      loadQuiz();
    }
  }, [quizId]);

  const handleSelectOption = (questionIndex: number, optionKey: string) => {
    if (isReview) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionIndex]: optionKey,
    }));
  };

  const handleSubmit = async () => {
    if (!quiz) return;
    
    // Kiểm tra xem đã trả lời hết chưa
    const answeredCount = Object.keys(selectedAnswers).length;
    if (answeredCount < quiz.total_questions) {
      if (!confirm(`Bạn mới trả lời ${answeredCount}/${quiz.total_questions} câu hỏi. Vẫn muốn nộp bài?`)) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const answersPayload = quiz.questions.map((q, idx) => ({
        question_index: idx,
        answer: selectedAnswers[idx] || "",
        is_correct: false, // Backend tự đối chiếu để cập nhật
      }));

      const payload = {
        answers: answersPayload,
        duration_seconds: duration,
      };

      const res = await apiClient.post(`/quizzes/${quizId}/submit`, payload);
      setAttemptResult(res.data);
      toast.success("Nộp bài thi thành công!");
      // Reload lại trang để chuyển sang chế độ Review (đáp án & giải thích)
      loadQuiz();
    } catch (err: any) {
      toast.error("Lỗi khi nộp bài thi. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500">Đang đồng bộ dữ liệu bài thi...</p>
      </div>
    );
  }

  if (!quiz) return null;

  const currentQuestion = quiz.questions[currentQuestionIndex];

  return (
    <div className="space-y-6 text-left max-w-4xl mx-auto">
      {/* Header Info */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-bold text-indigo-650 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-lg uppercase tracking-wide">
            Độ khó: {quiz.difficulty}
          </span>
          <h1 className="text-xl font-black text-zinc-900 dark:text-white mt-2">{quiz.title}</h1>
        </div>

        {/* Trạng thái hiển thị */}
        {isReview ? (
          <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-4 py-2 rounded-xl text-xs font-bold">
            <Trophy className="w-4 h-4" />
            Đã hoàn thành luyện tập
          </div>
        ) : (
          <div className="flex items-center gap-2 text-indigo-650 bg-indigo-50 dark:bg-indigo-950/40 px-4 py-2 rounded-xl text-xs font-bold">
            <Clock className="w-4 h-4" />
            Thời gian: {Math.floor(duration / 60)}p {duration % 60}s
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cột trái: Câu hỏi hiện tại */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between min-h-[400px]">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800 mb-6">
              <span className="text-xs font-bold text-zinc-400">
                Câu hỏi {currentQuestionIndex + 1} / {quiz.total_questions}
              </span>
            </div>

            <h3 className="text-base font-extrabold text-zinc-850 dark:text-zinc-100 leading-relaxed mb-6">
              {currentQuestion.question_text}
            </h3>

            {/* Danh sách lựa chọn */}
            <div className="space-y-3">
              {currentQuestion.options.map((opt) => {
                const isSelected = selectedAnswers[currentQuestionIndex] === opt.key;
                const isCorrect = currentQuestion.correct_answer === opt.key;
                
                // Styles tương ứng các trạng thái
                let optionStyle = "border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-zinc-350 dark:hover:border-zinc-700";
                if (!isReview && isSelected) {
                  optionStyle = "border-indigo-600 dark:border-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400";
                } else if (isReview) {
                  if (isCorrect) {
                    optionStyle = "border-emerald-600 dark:border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400";
                  } else if (isSelected && !isCorrect) {
                    optionStyle = "border-red-650 dark:border-red-500 bg-red-50/10 dark:bg-red-950/20 text-red-650 dark:text-red-400";
                  }
                }

                return (
                  <button
                    key={opt.key}
                    onClick={() => handleSelectOption(currentQuestionIndex, opt.key)}
                    disabled={isReview}
                    className={`w-full flex items-start gap-4 p-4 border rounded-xl text-left transition-all ${optionStyle}`}
                  >
                    <span className="font-extrabold text-sm">{opt.key}.</span>
                    <span className="text-sm font-semibold">{opt.value}</span>
                  </button>
                );
              })}
            </div>

            {/* AI Explanation block ở chế độ review */}
            {isReview && currentQuestion.explanation && (
              <div className="mt-8 p-5 bg-indigo-50/30 dark:bg-zinc-950/30 border border-indigo-100/50 dark:border-zinc-800 rounded-xl space-y-2">
                <h4 className="text-xs font-bold text-indigo-650 dark:text-indigo-400 uppercase tracking-wider">Giải thích đáp án AI</h4>
                <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                  {currentQuestion.explanation}
                </p>
              </div>
            )}
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between pt-6 border-t border-zinc-100 dark:border-zinc-800 mt-8">
            <button
              onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentQuestionIndex === 0}
              className="px-4 py-2 border border-zinc-200 dark:border-zinc-700 disabled:opacity-30 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
              Câu trước
            </button>

            {currentQuestionIndex < quiz.total_questions - 1 ? (
              <button
                onClick={() => setCurrentQuestionIndex((prev) => Math.min(quiz.total_questions - 1, prev + 1))}
                className="px-4 py-2 bg-zinc-800 dark:bg-zinc-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
              >
                Câu sau
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : !isReview ? (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-md shadow-indigo-500/10"
              >
                <Send className="w-3.5 h-3.5" />
                Nộp bài thi
              </button>
            ) : (
              <button
                onClick={() => router.push("/student/quizzes")}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Quay lại kho
              </button>
            )}
          </div>
        </div>

        {/* Cột phải: Bản đồ câu hỏi nhanh */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-6">
          <div>
            <h3 className="font-extrabold text-xs text-zinc-400 uppercase tracking-wider border-b border-zinc-100 dark:border-zinc-800 pb-3 mb-4">
              Bản đồ câu hỏi
            </h3>
            <div className="flex flex-wrap gap-2.5">
              {quiz.questions.map((_, idx) => {
                const isSelected = selectedAnswers[idx] !== undefined;
                const isCurrent = currentQuestionIndex === idx;

                let btnStyle = "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";
                if (isCurrent) {
                  btnStyle = "border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50/20";
                } else if (isSelected) {
                  btnStyle = "border-zinc-400 dark:border-zinc-600 text-zinc-800 dark:text-zinc-100 bg-zinc-50 dark:bg-zinc-800";
                }

                return (
                  <button
                    key={idx}
                    onClick={() => setCurrentQuestionIndex(idx)}
                    className={`w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle}`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
