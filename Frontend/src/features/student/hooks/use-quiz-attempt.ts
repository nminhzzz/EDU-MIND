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
  const [essayFilePath, setEssayFilePath] = useState<string | null>(null);
  const [uploadingEssay, setUploadingEssay] = useState(false);

  const handleUploadEssay = useCallback(async (file: File) => {
    setUploadingEssay(true);
    try {
      const res = await quizService.uploadEssay(file);
      setEssayFilePath(res.data.file_path);
      toast.success("Tải tệp tự luận lên thành công!");
    } catch {
      toast.error("Không thể tải tệp tự luận lên.");
    } finally {
      setUploadingEssay(false);
    }
  }, []);

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

    // Kiểm tra câu tự luận và tải file bài làm
    const hasEssay = quiz.questions.some(q => q.question_type === "essay");
    if (hasEssay && !essayFilePath) {
      if (!confirm("Đề thi này có phần câu hỏi tự luận nhưng bạn chưa tải lên file bài làm. Bạn vẫn muốn nộp bài?")) {
        return;
      }
    }

    const mcqQuestions = quiz.questions.filter(q => q.question_type !== "essay");
    const answeredMcqCount = mcqQuestions.filter((_, idx) => {
      const originalIdx = quiz.questions.findIndex(q => q === mcqQuestions[idx]);
      return !!selectedAnswers[originalIdx];
    }).length;

    if (answeredMcqCount < mcqQuestions.length) {
      if (
        !confirm(
          `Bạn mới trả lời ${answeredMcqCount}/${mcqQuestions.length} câu hỏi trắc nghiệm. Vẫn muốn nộp bài?`,
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
        essay_file_path: essayFilePath || undefined,
      });
      toast.success("Nộp bài thi thành công!");
      await loadQuiz();
    } catch {
      toast.error("Lỗi khi nộp bài thi. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }, [quiz, quizId, selectedAnswers, duration, loadQuiz, confirm, essayFilePath]);

  const mcqQuestions = quiz ? quiz.questions.filter((q) => q.question_type !== "essay") : [];
  const essayQuestions = quiz ? quiz.questions.filter((q) => q.question_type === "essay") : [];
  const totalPages = isReview
    ? (quiz ? quiz.questions.length : 0)
    : (mcqQuestions.length + (essayQuestions.length > 0 ? 1 : 0));

  const goToPreviousQuestion = useCallback(() => {
    setCurrentQuestionIndex((prev) => Math.max(0, prev - 1));
  }, []);

  const goToNextQuestion = useCallback(() => {
    if (!quiz) return;
    setCurrentQuestionIndex((prev) => Math.min(totalPages - 1, prev + 1));
  }, [quiz, totalPages]);

  const goToQuestion = useCallback((index: number) => {
    if (isReview) {
      setCurrentQuestionIndex(index);
    } else {
      if (index >= mcqQuestions.length) {
        setCurrentQuestionIndex(mcqQuestions.length);
      } else {
        setCurrentQuestionIndex(index);
      }
    }
  }, [isReview, mcqQuestions.length]);

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
    essayFilePath,
    uploadingEssay,
    handleUploadEssay,
  };
}
