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
  const loadedRef = useRef<string | number | null>(null);

  // Cấu hình thời gian & giới hạn vi phạm
  const timeLimit = quiz
    ? (quiz.time_limit_minutes ? quiz.time_limit_minutes * 60 : quiz.total_questions * (quiz.difficulty === "easy" ? 60 : quiz.difficulty === "hard" ? 120 : 90))
    : 0;
  const timeRemaining = quiz ? Math.max(0, timeLimit - duration) : 0;

  const handleUploadEssay = useCallback(async (file: File) => {
    setUploadingEssay(true);
    try {
      if (!quizId) throw new Error("Missing quiz id");
      const res = await quizService.uploadEssay(file, quizId);
      setEssayFilePath(res.data.file_path);
      toast.success("Tải tệp tự luận lên thành công!");
    } catch {
      toast.error("Không thể tải tệp tự luận lên.");
    } finally {
      setUploadingEssay(false);
    }
  }, [quizId]);

  const loadQuiz = useCallback(async (force = false) => {
    if (!quizId) return;
    if (!force && loadedRef.current === quizId) return;

    loadedRef.current = quizId;
    setLoading(true);
    try {
      const reviewRes = await quizService.getReview(quizId);
      const quizData = normalizeQuiz(reviewRes.data);
      setQuiz(quizData);
      setIsReview(true);

      // Nạp danh sách câu trả lời học sinh đã chọn từ lượt làm bài gần nhất
      const userAnswers = quizData.latest_attempt?.answers || (quizData.latest_attempt as any)?.student_answers;
      if (userAnswers && Array.isArray(userAnswers)) {
        const answersMap: Record<number, string> = {};
        userAnswers.forEach((sa: any) => {
          if (sa.question_index !== undefined && sa.answer !== undefined) {
            answersMap[sa.question_index] = sa.answer;
          }
        });
        setSelectedAnswers(answersMap);
      }
    } catch {
      try {
        const quizRes = await quizService.getById(quizId);
        const quizData = normalizeQuiz(quizRes.data);

        if (quizData.deadline && new Date(quizData.deadline).getTime() < Date.now()) {
          toast.error("Đề thi này đã quá hạn chót nộp bài! Bạn không thể làm nữa.");
          router.push(ROUTES.STUDENT_QUIZZES);
          return;
        }

        setQuiz(quizData);
        setIsReview(false);
        setDuration(0);
        setTabViolations(0);
      } catch (err: any) {
        const msg = err?.response?.data?.detail || "Không thể tải thông tin đề thi.";
        toast.error(msg);
        router.push(ROUTES.STUDENT_QUIZZES);
      }
    } finally {
      setLoading(false);
    }
  }, [quizId, router]);

  useEffect(() => {
    loadQuiz();
  }, [loadQuiz]);

  // Polling ngầm để cập nhật nhận xét AI khi bài làm vừa được chấm xong
  const [needsAiPolling, setNeedsAiPolling] = useState(false);

  useEffect(() => {
    // Kích hoạt polling khi vào review mode mà chưa có ai_assessment
    if (isReview && quiz?.latest_attempt && !quiz.latest_attempt.ai_assessment) {
      const submittedAt = quiz.latest_attempt.submitted_at as string | undefined;
      if (submittedAt) {
        // Backend trả submitted_at dạng UTC nhưng thiếu 'Z' → append 'Z' để JS parse đúng timezone
        const utcDate = submittedAt.endsWith("Z") ? submittedAt : submittedAt + "Z";
        const elapsed = Date.now() - new Date(utcDate).getTime();
        if (elapsed < 120_000) {
          setNeedsAiPolling(true);
        }
      }
    }
  }, [isReview, quiz?.latest_attempt?.ai_assessment]);

  useEffect(() => {
    if (!needsAiPolling || !quiz) return;

    let pollCount = 0;
    const maxPolls = 30;
    let cancelled = false;

    const timer = setInterval(async () => {
      if (cancelled) return;
      pollCount++;
      if (pollCount > maxPolls) {
        clearInterval(timer);
        setNeedsAiPolling(false);
        return;
      }

      try {
        const reviewRes = await quizService.getReview(quiz.id);
        const quizData = normalizeQuiz(reviewRes.data);
        if (quizData.latest_attempt?.ai_assessment) {
          setQuiz(quizData);
          clearInterval(timer);
          setNeedsAiPolling(false);
        }
      } catch {
        // Ignored polling errors
      }
    }, 3000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [needsAiPolling, quiz?.id]);

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
      await loadQuiz(true);
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
      // Tạm dừng cảnh báo rời tab khi học sinh đang làm phần Tự luận hoặc đang tải tệp
      const mcqCount = quiz.questions.filter((q) => q.question_type !== "essay").length;
      const currentQ = quiz.questions[currentQuestionIndex];
      const isEssaySection = !currentQ || currentQ.question_type === "essay" || currentQuestionIndex >= mcqCount;

      if (isEssaySection || uploadingEssay) {
        return; // Không đếm vi phạm khi ở phần Tự luận
      }

      const now = Date.now();
      if (now - lastViolationTimeRef.current < 1000) return;
      lastViolationTimeRef.current = now;

      const maxAllowed = quiz.max_tab_violations ?? 3;
      setTabViolations((prev) => {
        const next = prev + 1;
        if (maxAllowed > 0 && next >= maxAllowed) {
          toast.error(`Bạn đã vi phạm quy chế thi (thoát tab quá ${maxAllowed} lần). Bài thi sẽ tự động được nộp!`);
          handleSubmit(true);
        } else if (maxAllowed > 0) {
          toast.warning(`Cảnh báo: Bạn vừa rời khỏi màn hình làm bài thi ${next}/${maxAllowed} lần!`);
        } else {
          toast.warning(`Cảnh báo: Bạn vừa rời khỏi màn hình làm bài thi ${next} lần!`);
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
  }, [loading, isReview, quiz, handleSubmit, currentQuestionIndex, uploadingEssay]);

  // Cảnh báo & Tự động nộp bài khi cố tình rời trang hoặc bấm sang tab khác trong ứng dụng
  useEffect(() => {
    if (loading || isReview || !quiz || submitting) return;

    // 1. Cảnh báo khi đóng tab hoặc reload trình duyệt
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "Bạn đang làm bài thi. Nếu rời khỏi, bài làm sẽ tự động nộp!";
      return e.returnValue;
    };

    // 2. Chặn các cú nhấp chuột chuyển trang trong ứng dụng (Sidebar, Header, Links)
    const handleAnchorClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest("a");
      if (!target) return;

      const href = target.getAttribute("href");
      if (href && !href.startsWith("#") && !href.includes(`/student/quizzes/${quizId}`)) {
        e.preventDefault();
        e.stopPropagation();

        const confirmed = window.confirm(
          "⚠️ CẢNH BÁO LÀM BÀI THI:\n\nBạn đang trong quá trình làm bài kiểm tra! Bạn có chắc chắn muốn rời khỏi trang này không?\n\nNếu bạn chọn ĐỒNG Ý, bài thi của bạn sẽ tự động được NỘP NGAY LẬP TỨC."
        );

        if (confirmed) {
          handleSubmit(true).then(() => {
            router.push(href);
          });
        }
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    document.addEventListener("click", handleAnchorClick, true);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      document.removeEventListener("click", handleAnchorClick, true);
    };
  }, [loading, isReview, quiz, submitting, quizId, handleSubmit, router]);

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
