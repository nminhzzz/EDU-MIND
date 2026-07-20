"use client";

import React, { useState, useEffect, useRef } from "react";
import { quizService } from "@/features/student/services/quiz";
import type { QuizAttemptResult, StudentQuiz } from "@/features/student/types";
import { toast } from "sonner";
import { Loader2, HelpCircle, CheckCircle2, XCircle, Trophy, UploadCloud, Sparkles } from "lucide-react";

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
  const [essayFilePath, setEssayFilePath] = useState<string | null>(null);
  const [uploadingEssay, setUploadingEssay] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUploadEssay = async (file: File) => {
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
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    try {
      const res = await quizService.generateForPlan(studyPlanId);
      setQuiz(toStudentQuiz(res.data));
      setStartTime(Date.now());
      toast.success("AI đã sinh đề kiểm tra nhanh thành công!");
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Không thể sinh đề kiểm tra AI.";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

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


  const handleSelectAnswer = (ansKey: string) => {
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentIdx]: ansKey,
    }));
  };

  const mcqQuestions = quiz ? quiz.questions.filter((q) => q.question_type !== "essay") : [];
  const essayQuestions = quiz ? quiz.questions.filter((q) => q.question_type === "essay") : [];
  const totalPages = mcqQuestions.length + (essayQuestions.length > 0 ? 1 : 0);

  const handleNext = () => {
    if (!quiz) return;
    if (currentIdx < totalPages - 1) {
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

    // Kiểm tra câu tự luận và tải file bài làm
    const hasEssay = quiz.questions.some((q) => q.question_type === "essay");
    if (hasEssay && !essayFilePath) {
      if (!window.confirm("Nhiệm vụ này có câu hỏi tự luận nhưng bạn chưa tải lên file bài làm. Bạn vẫn muốn nộp bài?")) {
        return;
      }
    }

    // Đảm bảo học sinh đã chọn đáp án cho tất cả câu hỏi MCQ
    const mcqQuestions = quiz.questions.filter((q) => q.question_type !== "essay");
    const answeredMcqCount = mcqQuestions.filter((_, idx) => {
      const originalIdx = quiz.questions.findIndex((q) => q === mcqQuestions[idx]);
      return !!selectedAnswers[originalIdx];
    }).length;

    if (answeredMcqCount < mcqQuestions.length) {
      toast.error(`Vui lòng trả lời đầy đủ ${mcqQuestions.length} câu hỏi trắc nghiệm trước khi nộp bài.`);
      return;
    }

    setSubmitting(true);
    const duration = Math.round((Date.now() - startTime) / 1000);

    try {
      const res = await quizService.submit(quiz.id, {
        answers: quiz.questions.map((_, idx) => ({
          question_index: idx,
          answer: selectedAnswers[idx] || "",
        })),
        duration_seconds: duration,
        tab_violations_count: 0,
        essay_file_path: essayFilePath || undefined,
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
      <div className="flex flex-col items-center justify-center text-center p-6 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 space-y-4">
        <HelpCircle className="w-10 h-10 text-indigo-500 mb-1 opacity-80" />
        <div>
          <h4 className="text-sm font-extrabold text-zinc-850 dark:text-zinc-200">Đánh giá nhanh lý thuyết</h4>
          <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-1 max-w-xs leading-relaxed font-semibold">
            Nhiệm vụ này chưa được tạo đề kiểm tra nhanh. Bạn có muốn kích hoạt AI sinh đề kiểm tra ngay bây giờ không?
          </p>
        </div>
        <button
          onClick={handleGenerateQuiz}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white rounded-xl shadow-md cursor-pointer flex items-center justify-center gap-1.5 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5" />
          Sinh đề thi bằng AI ⚡
        </button>
      </div>
    );
  }

  // 2. Đã có kết quả nộp bài
  if (result) {
    const isPass = result.score >= 5.0;
    return (
      <div className="border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 overflow-hidden flex flex-col text-left">
        {/* Score Summary Banner */}
        <div className="flex flex-col items-center justify-center text-center p-6 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 space-y-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isPass ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" : "bg-red-500/10 text-red-500 border border-red-500/20"
          }`}>
            <Trophy className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-black text-zinc-800 dark:text-zinc-200 uppercase">KẾT QUẢ KIỂM TRA</h4>
            <span className={`inline-block mt-1.5 px-3 py-0.5 rounded-full text-xs font-black ${
              isPass ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40" : "text-red-600 bg-red-50 dark:bg-red-950/40"
            }`}>
              {result.score.toFixed(1)} / 10 Điểm
            </span>
            <div className="flex items-center justify-center gap-3 mt-2 text-[10px] font-bold text-zinc-500">
              <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-emerald-500" /> Đúng: {result.correct_count}</span>
              <span className="flex items-center gap-1"><XCircle className="w-3 h-3 text-red-400" /> Sai: {result.wrong_count}</span>
            </div>
          </div>
        </div>

        {/* Detailed Question Review List */}
        <div className="p-4 space-y-4 max-h-[350px] overflow-y-auto">
          <h5 className="text-[10px] font-black text-zinc-400 uppercase tracking-wider mb-2">CHI TIẾT ĐÁP ÁN ĐÃ CHẤM</h5>
          {quiz.questions.map((q, idx) => {
            const attemptAns = result.answers?.find((a: any) => a.question_index === idx);
            const isQCorrect = attemptAns?.is_correct;
            const qType = q.question_type || "mcq";

            return (
              <div key={idx} className="p-3 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-xl space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] font-black text-zinc-400">Câu {idx + 1} ({qType === "essay" ? "Tự luận" : "Trắc nghiệm"})</span>
                  <span className={`px-1.5 py-0.5 rounded text-[8px] font-extrabold uppercase ${
                    isQCorrect
                      ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400"
                      : "bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400"
                  }`}>
                    {qType === "essay" 
                      ? `${attemptAns?.score ?? 0} đ`
                      : isQCorrect ? "Đúng" : "Sai"
                    }
                  </span>
                </div>
                
                <p className="text-[11px] font-bold text-zinc-850 dark:text-zinc-200">{q.question_text}</p>

                {qType === "essay" ? (
                  <div className="space-y-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                    <div className="bg-zinc-50 dark:bg-zinc-950/40 p-2 rounded text-[10px]">
                      <span className="font-extrabold text-zinc-400 block uppercase tracking-wider text-[8px] mb-0.5">Bài làm của bạn (Trích xuất OCR):</span>
                      <p className="font-semibold text-zinc-700 dark:text-zinc-350 italic">"{attemptAns?.answer || "[Không tìm thấy bài viết]"}"</p>
                    </div>

                    <div className="bg-indigo-50/20 dark:bg-indigo-950/15 p-2 rounded text-[10px] border border-indigo-500/10">
                      <span className="font-extrabold text-indigo-650 dark:text-indigo-400 block uppercase tracking-wider text-[8px] mb-0.5 flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5" /> Lời phê AI Grader:
                      </span>
                      <p className="font-semibold text-zinc-700 dark:text-zinc-300">{attemptAns?.feedback || "Chưa có nhận xét."}</p>
                    </div>

                    <div className="bg-emerald-50/10 dark:bg-emerald-950/5 p-2 rounded text-[10px]">
                      <span className="font-extrabold text-emerald-600 block uppercase tracking-wider text-[8px] mb-0.5">Đáp án mẫu / gợi ý giải:</span>
                      <p className="font-semibold text-zinc-600 dark:text-zinc-400">{q.correct_answer}</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-1.5 pt-1.5 text-[10px] border-t border-zinc-100 dark:border-zinc-800">
                    <div className="flex gap-2">
                      <span className="font-bold text-zinc-400">Đã chọn:</span>
                      <span className="font-extrabold text-zinc-700 dark:text-zinc-300">{attemptAns?.answer || "[Không trả lời]"}</span>
                    </div>
                    <div className="flex gap-2">
                      <span className="font-bold text-emerald-600">Đáp án đúng:</span>
                      <span className="font-extrabold text-emerald-600">{q.correct_answer}</span>
                    </div>
                    {q.explanation && (
                      <div className="mt-1 bg-zinc-50 dark:bg-zinc-950/20 p-2 rounded text-zinc-500">
                        <span className="font-bold block text-[8px] uppercase">Giải thích:</span>
                        <p className="font-semibold">{q.explanation}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // 3. Đang làm bài
  const activeQuestion = currentIdx < mcqQuestions.length ? mcqQuestions[currentIdx] : null;
  const progress = ((currentIdx + 1) / totalPages) * 100;

  return (
    <div className="border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 overflow-hidden text-left flex flex-col">
      {/* Tiêu đề & Tiến trình */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md font-mono uppercase">
            {quiz.title}
          </span>
          <span className="text-[10px] text-zinc-400 dark:text-zinc-550 font-bold">
            {currentIdx < mcqQuestions.length
              ? `Câu ${currentIdx + 1}/${quiz.questions.length}`
              : "Phần Tự luận"
            }
          </span>
        </div>
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-indigo-600 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {/* Nội dung câu hỏi & Câu trả lời */}
      <div className="p-5 flex-1 space-y-4">
        {currentIdx === mcqQuestions.length ? (
          <div className="space-y-4">
            {/* List of all essay questions grouped */}
            <div className="space-y-3">
              {essayQuestions.map((q, idx) => {
                const originalIndex = quiz.questions.findIndex((originalQ) => originalQ === q);
                return (
                  <div key={idx} className="p-3.5 bg-white dark:bg-zinc-900 border border-zinc-200/70 dark:border-zinc-800 rounded-xl space-y-1">
                    <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wide">
                      Câu hỏi tự luận {idx + 1} (Câu {originalIndex + 1} trong đề)
                    </span>
                    <p className="text-xs font-bold text-zinc-850 dark:text-zinc-200 leading-relaxed">
                      {q.question_text}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Single file upload box */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleUploadEssay(e.target.files[0]);
                }
              }}
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
              className="hidden"
            />

            <div
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer flex flex-col items-center justify-center space-y-3 ${
                essayFilePath
                  ? "border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/5"
                  : "border-zinc-300 dark:border-zinc-700 hover:border-indigo-500 dark:hover:border-indigo-400 bg-zinc-50/50 dark:bg-zinc-950/20"
              }`}
            >
              {uploadingEssay ? (
                <div className="flex flex-col items-center space-y-2">
                  <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
                  <p className="text-[10px] font-bold text-zinc-500">Đang tải và xử lý file bài làm...</p>
                </div>
              ) : essayFilePath ? (
                <div className="flex flex-col items-center space-y-1 animate-fadeIn">
                  <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400">Đã nhận tệp bài làm!</p>
                  <p className="text-[10px] text-zinc-500 font-semibold max-w-xs truncate">
                    {essayFilePath.split(/[\\/]/).pop()}
                  </p>
                  <span className="text-[10px] text-zinc-400 font-medium mt-1 hover:underline">
                    Chọn tệp khác để thay thế
                  </span>
                </div>
              ) : (
                <>
                  <div className="p-2 bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-650 rounded-full">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div className="space-y-0.5">
                    <p className="text-[10px] font-bold text-zinc-700 dark:text-zinc-300">
                      Click để chọn hoặc kéo thả tệp bài làm tự luận
                    </p>
                    <p className="text-[9px] text-zinc-400 font-medium">
                      Hỗ trợ ảnh viết tay (.png, .jpg), PDF, Word (.docx) hoặc TXT
                    </p>
                  </div>
                </>
              )}
            </div>

            <div className="p-3.5 bg-indigo-50/30 dark:bg-indigo-950/10 border border-indigo-100/30 dark:border-indigo-900/20 rounded-xl">
              <p className="text-[10px] text-zinc-500 dark:text-zinc-400 font-medium leading-relaxed">
                💡 <span className="font-bold text-indigo-600">Lưu ý quan trọng:</span> Bạn chỉ cần tải lên **01 tệp duy nhất** chứa toàn bộ lời giải của tất cả các câu hỏi tự luận trên. AI Grader sẽ tự động trích xuất OCR và chấm chi tiết từng câu.
              </p>
            </div>
          </div>
        ) : (
          activeQuestion && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-zinc-850 dark:text-zinc-100 leading-relaxed">
                {activeQuestion.question_text}
              </h4>
              <div className="space-y-2">
                {activeQuestion.options?.map((opt) => {
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
          )
        )}
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

        {currentIdx < totalPages - 1 ? (
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
