"use client";

import React, { useState, useEffect } from "react";
import { quizService } from "@/features/student/services/quiz";
import type { QuizAttemptResult, StudentQuiz } from "@/features/student/types";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";
import { Loader2, HelpCircle, CheckCircle2, XCircle, Trophy } from "lucide-react";

interface QuickQuizPaneProps {
  subjectId: number;
  topic: string;
  studyPlanId: number;
  onSuccess?: () => void;
}

function toStudentQuiz(data: {
  id: number;
  title: string;
  questions?: StudentQuiz["questions"];
  difficulty?: string;
  total_questions?: number;
}): StudentQuiz {
  const questions = data.questions ?? [];
  return {
    id: data.id,
    title: data.title,
    difficulty: data.difficulty,
    questions,
    total_questions: data.total_questions ?? questions.length,
  };
}

export function QuickQuizPane({ subjectId, topic, studyPlanId, onSuccess }: QuickQuizPaneProps) {
  const [checkingExisting, setCheckingExisting] = useState(true);
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState<StudentQuiz | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<QuizAttemptResult | null>(null);
  const [startTime, setStartTime] = useState<number>(0);

  // Kiểm tra xem đã có đề thi trắc nghiệm được liên kết sẵn với task này chưa
  useEffect(() => {
    let active = true;
    const fetchExistingQuiz = async () => {
      try {
        const res = await quizService.getByPlanId(studyPlanId);
        if (active) {
          setQuiz(toStudentQuiz(res.data));
          setStartTime(Date.now());
        }
      } catch (err) {
        // 404 -> Chưa có đề thi được sinh sẵn cho nhiệm vụ cụ thể này
        console.log("Chưa có đề thi liên kết với task:", studyPlanId);
      } finally {
        if (active) setCheckingExisting(false);
      }
    };
    fetchExistingQuiz();
    return () => {
      active = false;
    };
  }, [studyPlanId]);

  // Gọi API sinh đề trắc nghiệm nhanh 3 câu
  const handleGenerate = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const res = await quizService.generate({
        subject_id: subjectId,
        topic,
        difficulty: "medium",
        total_questions: 5,
        study_plan_id: studyPlanId,
      });
      setQuiz(toStudentQuiz(res.data));
      setStartTime(Date.now());
    } catch (err: unknown) {
      console.error("Lỗi sinh đề nhanh:", err);
      toast.error(parseApiError(err, "Không thể khởi tạo đề kiểm tra nhanh."));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAnswer = (ansKey: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentIdx]: ansKey,
    }));
  };

  const handleNext = () => {
    if (!quiz) return;
    if (currentIdx < quiz.questions.length - 1) {
      setCurrentIdx((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx((prev) => prev - 1);
    }
  };

  // Nộp bài thi
  const handleSubmit = async () => {
    if (!quiz) return;
    
    // Đảm bảo học sinh đã chọn đáp án cho tất cả câu hỏi
    if (Object.keys(selectedAnswers).length < quiz.questions.length) {
      toast.error("Vui lòng trả lời đầy đủ các câu hỏi trước khi nộp bài.");
      return;
    }

    setSubmitting(true);
    const duration = Math.round((Date.now() - startTime) / 1000);

    try {
      const res = await quizService.submit(quiz.id, {
        answers: Object.entries(selectedAnswers).map(([idx, ans]) => ({
          question_index: parseInt(idx, 10),
          answer: ans,
        })),
        duration_seconds: duration,
      });
      setResult(res.data);
      toast.success("Nộp bài thi thành công!");
      if (onSuccess) {
        onSuccess(); // Thông báo cho modal chính biết nhiệm vụ có thể hoàn thành
      }
    } catch (err: unknown) {
      console.error("Lỗi nộp bài thi:", err);
      toast.error("Nộp bài thất bại. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  };

  if (checkingExisting) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-400 gap-2">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <span className="text-xs font-semibold">Đang tìm đề thi liên kết...</span>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-400 gap-2">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <span className="text-xs font-semibold">AI đang sinh câu hỏi (thường mất 30–90 giây)...</span>
      </div>
    );
  }

  // 1. Chưa sinh quiz
  if (!quiz) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-6 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20">
        <HelpCircle className="w-10 h-10 text-indigo-500 mb-3 opacity-80" />
        <h4 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-200">Đánh giá nhanh lý thuyết</h4>
        <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-1 max-w-xs leading-relaxed font-semibold">
          AI sẽ sinh 5 câu hỏi trắc nghiệm theo chủ đề này để bạn kiểm tra nhanh kết quả nghiên cứu. Cần đạt ≥ 8/10 điểm để hoàn thành nhiệm vụ.
        </p>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-extrabold rounded-lg transition-transform active:scale-[0.98] cursor-pointer shadow-md shadow-indigo-500/10 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          Bắt đầu kiểm tra trắc nghiệm nhanh 📝
        </button>
      </div>
    );
  }

  // 2. Đã có kết quả nộp bài
  if (result) {
    const isPass = result.score >= 5.0;
    return (
      <div className="flex flex-col items-center justify-center text-center p-6 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 space-y-4">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
          isPass ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" : "bg-red-500/10 text-red-500 border border-red-500/20"
        }`}>
          <Trophy className="w-6 h-6" />
        </div>
        <div>
          <h4 className="text-sm font-black text-zinc-800 dark:text-zinc-200 uppercase">KẾT QUẢ KIỂM TRA</h4>
          <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm font-black ${
            isPass ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40" : "text-red-600 bg-red-50 dark:bg-red-950/40"
          }`}>
            {result.score.toFixed(1)} / 10 Điểm
          </span>
          <div className="flex items-center justify-center gap-4 mt-3 text-xs font-semibold text-zinc-550 dark:text-zinc-400">
            <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Đúng: {result.correct_count}</span>
            <span className="flex items-center gap-1"><XCircle className="w-3.5 h-3.5 text-red-400" /> Sai: {result.wrong_count}</span>
          </div>
        </div>
      </div>
    );
  }

  // 3. Đang làm bài
  const activeQuestion = quiz.questions[currentIdx];
  const progress = ((currentIdx + 1) / quiz.questions.length) * 100;

  return (
    <div className="border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 overflow-hidden text-left flex flex-col">
      {/* Tiêu đề & Tiến trình */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md font-mono uppercase">
            {quiz.title}
          </span>
          <span className="text-[10px] text-zinc-400 dark:text-zinc-550 font-bold">
            Câu {currentIdx + 1}/{quiz.questions.length}
          </span>
        </div>
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-indigo-600 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Nội dung câu hỏi & Câu trả lời */}
      <div className="p-5 flex-1 space-y-4">
        <h4 className="text-xs font-bold text-zinc-800 dark:text-zinc-200 leading-relaxed">
          {activeQuestion.question_text}
        </h4>
        <div className="space-y-2">
          {activeQuestion.options.map((opt) => {
            const isSelected = selectedAnswers[currentIdx] === opt.key;
            return (
              <button
                key={opt.key}
                onClick={() => handleSelectAnswer(opt.key)}
                className={`w-full p-3 text-left text-xs rounded-xl border transition-all cursor-pointer flex gap-3 ${
                  isSelected
                    ? "bg-indigo-50 dark:bg-indigo-950/40 border-indigo-400 dark:border-indigo-600 text-indigo-700 dark:text-indigo-300 font-extrabold"
                    : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-350 hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
                }`}
              >
                <span className={`w-5 h-5 rounded-md flex items-center justify-center text-[10px] font-bold border transition-colors ${
                  isSelected
                    ? "bg-indigo-600 border-indigo-600 text-white"
                    : "bg-zinc-50 dark:bg-zinc-855 border-zinc-200 dark:border-zinc-700 text-zinc-400"
                }`}>
                  {opt.key}
                </span>
                <span className="flex-1 font-semibold">{opt.value}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Điều hướng */}
      <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex justify-between gap-4">
        <button
          onClick={handlePrev}
          disabled={currentIdx === 0}
          className="px-3 py-1.5 border border-zinc-200 dark:border-zinc-750 text-[10px] font-bold rounded-lg text-zinc-500 hover:text-zinc-800 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-800 disabled:opacity-40 cursor-pointer"
        >
          Quay lại
        </button>

        {currentIdx < quiz.questions.length - 1 ? (
          <button
            onClick={handleNext}
            className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-[10px] font-bold text-white rounded-lg cursor-pointer"
          >
            Tiếp theo
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-[10px] font-bold text-white rounded-lg cursor-pointer disabled:opacity-55"
          >
            {submitting ? "Đang chấm..." : "Nộp bài thi ✔"}
          </button>
        )}
      </div>
    </div>
  );
}
