"use client";

import { useCallback, useEffect, useState, useRef } from "react";
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
  const [tabViolations, setTabViolations] = useState(0);

  const lastViolationTimeRef = useRef<number>(0);

  // Easy: 60s/câu, Hard: 120s/câu, Medium: 90s/câu
  const secondsPerQuestion = quiz ? (quiz.difficulty === "easy" ? 60 : quiz.difficulty === "hard" ? 120 : 90) : 90;
  const timeLimit = quiz ? quiz.total_questions * secondsPerQuestion : 0;
  const timeRemaining = quiz ? Math.max(0, timeLimit - duration) : 0;

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
        setTabViolations(0);
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

  // Tick elapsed time
  useEffect(() => {
    if (loading || isReview || !quiz) return;
    const interval = setInterval(() => {
      setDuration((prev) => {
        const next = prev + 1;
        if (timeLimit > 0 && next >= timeLimit) {
          clearInterval(interval);
        }
        return next;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [loading, isReview, quiz, timeLimit]);

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

  const handleSubmit = useCallback(async (isAutoSubmit = false) => {
    if (!quiz || !quizId) return;

    if (!isAutoSubmit) {
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
        tab_violations_count: tabViolations,
        essay_file_path: essayFilePath || undefined,
      });
      toast.success(isAutoSubmit ? "Hệ thống đã tự động nộp bài làm!" : "Nộp bài thi thành công!");
      await loadQuiz();
    } catch {
      toast.error("Lỗi khi nộp bài thi. Vui lòng thử lại.");
    } finally {
      setSubmitting(false);
    }
  }, [quiz, quizId, selectedAnswers, duration, tabViolations, loadQuiz, confirm, essayFilePath]);

  // Auto-submit when countdown hits zero
  useEffect(() => {
    if (loading || isReview || !quiz || timeLimit === 0) return;
    if (duration >= timeLimit) {
      toast.warning("Hết thời gian làm bài! Hệ thống tự động nộp bài.");
      handleSubmit(true);
    }
  }, [duration, timeLimit, loading, isReview, quiz, handleSubmit]);

  // Anti-cheat visibility & focus monitoring
  useEffect(() => {
    if (loading || isReview || !quiz) return;

    const handleViolation = () => {
      const now = Date.now();
      if (now - lastViolationTimeRef.current < 1000) return;
      lastViolationTimeRef.current = now;

      setTabViolations((prev) => {
        const next = prev + 1;
        if (next >= 3) {
          toast.error("Bạn đã vi phạm quy chế thi (thoát tab quá 3 lần). Bài thi sẽ tự động được nộp!");
          handleSubmit(true);
        } else {
          toast.warning(`Cảnh báo: Bạn vừa rời khỏi màn hình làm bài thi ${next}/3 lần!`);
        }
        return next;
      });
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        handleViolation();
      }
    };

    const handleWindowBlur = () => {
      handleViolation();
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleWindowBlur);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleWindowBlur);
    };
  }, [loading, isReview, quiz, handleSubmit]);

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
    timeRemaining,
    timeLimit,
    tabViolations,
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
