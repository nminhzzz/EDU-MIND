"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/features/student/constants";
import { useConfirmDialog } from "@/features/student/hooks/use-confirm-dialog";
import { quizService } from "@/features/student/services/quiz";
import { StudentQuiz } from "@/features/student/types/quiz";
import { toast } from "sonner";

function normalizeQuiz(data: StudentQuiz): StudentQuiz {
  return {
    ...data,
    total_questions: data.total_questions ?? data.questions.length,
  };
}

export function useQuizAttempt(quizId: string | number | undefined) {
  const router = useRouter();
  const confirm = useConfirmDialog();

  const [quiz, setQuiz] = useState<StudentQuiz | null>(null);
  const [loading, setLoading] = useState(true);
  const [isReview, setIsReview] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [duration, setDuration] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  const loadQuiz = useCallback(async () => {
    if (!quizId) return;

    setLoading(true);
    try {
      const reviewRes = await quizService.getReview(quizId);
      setQuiz(normalizeQuiz(reviewRes.data));
      setIsReview(true);
    } catch {
      try {
        const quizRes = await quizService.getById(quizId);
        setQuiz(normalizeQuiz(quizRes.data));
        setIsReview(false);
        setDuration(0);
      } catch {
        toast.error("Không thể tải thông tin đề thi.");
        router.push(ROUTES.STUDENT_QUIZZES);
      }
    } finally {
      setLoading(false);
    }
  }, [quizId, router]);

  useEffect(() => {
    loadQuiz();
  }, [loadQuiz]);

  useEffect(() => {
    if (loading || isReview) return;
    const interval = setInterval(() => {
      setDuration((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [loading, isReview]);

  const handleSelectOption = useCallback(
    (questionIndex: number, optionKey: string) => {
      if (isReview) return;
      setSelectedAnswers((prev) => ({
        ...prev,
        [questionIndex]: optionKey,
      }));
    },
    [isReview],
  );

  const handleSubmit = useCallback(async () => {
    if (!quiz || !quizId) return;

    const answeredCount = Object.keys(selectedAnswers).length;
    if (answeredCount < quiz.total_questions) {
      if (
        !confirm(
          `Bạn mới trả lời ${answeredCount}/${quiz.total_questions} câu hỏi. Vẫn muốn nộp bài?`,
        )
      ) {
        return;
      }
    }

    setSubmitting(true);
    try {
      await quizService.submit(quizId, {
        answers: quiz.questions.map((_, idx) => ({
          question_index: idx,
          answer: selectedAnswers[idx] || "",
          is_correct: false,
        })),
        duration_seconds: duration,
      });
      toast.success("Nộp bài thi thành công!");
      await loadQuiz();
    } catch {
      toast.error("Lỗi khi nộp bài thi. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }, [quiz, quizId, selectedAnswers, duration, loadQuiz, confirm]);

  const goToPreviousQuestion = useCallback(() => {
    setCurrentQuestionIndex((prev) => Math.max(0, prev - 1));
  }, []);

  const goToNextQuestion = useCallback(() => {
    if (!quiz) return;
    setCurrentQuestionIndex((prev) => Math.min(quiz.total_questions - 1, prev + 1));
  }, [quiz]);

  const goToQuestion = useCallback((index: number) => {
    setCurrentQuestionIndex(index);
  }, []);

  const goBackToList = useCallback(() => {
    router.push(ROUTES.STUDENT_QUIZZES);
  }, [router]);

  return {
    quiz,
    loading,
    isReview,
    currentQuestionIndex,
    selectedAnswers,
    duration,
    submitting,
    handleSelectOption,
    handleSubmit,
    goToPreviousQuestion,
    goToNextQuestion,
    goToQuestion,
    goBackToList,
  };
}
