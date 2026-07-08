"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/features/student/constants";
import { quizService } from "@/features/student/services/quiz";
import {
  GenerateQuizFormState,
  GeneratedQuiz,
} from "@/features/student/types/quiz";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";

const DEFAULT_FORM: GenerateQuizFormState = {
  subject_id: "",
  topic: "",
  difficulty: "medium",
  total_questions: 5,
};

export function useGenerateQuiz(onClose: () => void) {
  const router = useRouter();
  const [generating, setGenerating] = useState(false);
  const [formData, setFormData] = useState<GenerateQuizFormState>(DEFAULT_FORM);

  const updateForm = useCallback((patch: Partial<GenerateQuizFormState>) => {
    setFormData((prev) => ({ ...prev, ...patch }));
  }, []);

  const resetForm = useCallback(() => {
    setFormData(DEFAULT_FORM);
  }, []);

  const handleGenerateQuiz = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!formData.subject_id || !formData.topic.trim()) {
        toast.error("Vui lòng nhập đầy đủ thông tin bắt buộc.");
        return;
      }

      setGenerating(true);
      try {
        const res = await quizService.generate({
          subject_id: parseInt(formData.subject_id, 10),
          topic: formData.topic.trim(),
          difficulty: formData.difficulty,
          total_questions: formData.total_questions,
        });
        const generatedQuiz: GeneratedQuiz = res.data;
        toast.success("AI đã sinh đề thành công! Bắt đầu làm bài.");
        onClose();
        router.push(ROUTES.STUDENT_QUIZ(generatedQuiz.id));
      } catch (err: unknown) {
        toast.error(parseApiError(err, "AI sinh đề thất bại."));
      } finally {
        setGenerating(false);
      }
    },
    [formData, onClose, router],
  );

  return {
    formData,
    generating,
    updateForm,
    resetForm,
    handleGenerateQuiz,
  };
}
