"use client";

import React, { useRef } from "react";
import { ChevronLeft, ChevronRight, RotateCcw, Send, FileText, UploadCloud, CheckCircle2, ShieldCheck, AlertCircle, Loader2, Sparkles } from "lucide-react";
import { StudentQuiz, StudentQuizQuestion } from "@/features/student/types/quiz";
import { MathRenderer } from "@/components/shared/math-renderer";

function getOptionStyle(
  isReview: boolean,
  isSelected: boolean,
  isCorrect: boolean,
): string {
  if (!isReview && isSelected) {
    return "border-indigo-600 dark:border-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400";
  }
  if (isReview) {
    if (isCorrect) {
      return "border-emerald-600 dark:border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400";
    }
    if (isSelected && !isCorrect) {
      return "border-red-650 dark:border-red-500 bg-red-50/10 dark:bg-red-950/20 text-red-650 dark:text-red-400";
    }
  }
  return "border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-zinc-350 dark:hover:border-zinc-700";
}

interface QuizQuestionPanelProps {
  quiz: StudentQuiz;
  question: StudentQuizQuestion | null;
  questionIndex: number;
  isReview: boolean;
  selectedAnswers: Record<number, string>;
  submitting: boolean;
  onSelectOption: (questionIndex: number, optionKey: string) => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
  onBackToList: () => void;
  essayFilePath?: string | null;
  uploadingEssay?: boolean;
  handleUploadEssay?: (file: File) => void;
}

export function QuizQuestionPanel({
  quiz,
  question,
  questionIndex,
  isReview,
  selectedAnswers,
  submitting,
  onSelectOption,
  onPrevious,
  onNext,
  onSubmit,
  onBackToList,
  essayFilePath,
  uploadingEssay,
  handleUploadEssay,
}: QuizQuestionPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const qType = question ? (question.question_type || "mcq") : "essay";

  const attemptAnswer = isReview && question
    ? quiz.latest_attempt?.answers?.find((a: any) => a.question_index === questionIndex)
    : null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && handleUploadEssay) {
      handleUploadEssay(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    if (!isReview && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const mcqQuestions = quiz.questions.filter((q) => q.question_type !== "essay");
  const essayQuestions = quiz.questions.filter((q) => q.question_type === "essay");
  const totalPages = isReview
    ? quiz.total_questions
    : (mcqQuestions.length + (essayQuestions.length > 0 ? 1 : 0));

  return (
    <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between min-h-[450px]">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800 mb-6">
          <span className="text-xs font-bold text-zinc-400">
            {question
              ? `Câu hỏi ${questionIndex + 1} / ${quiz.total_questions}`
              : "Phần 2: Tự luận"
            }
          </span>
          <span className="px-2.5 py-1 text-[10px] font-bold tracking-wider uppercase bg-zinc-100 dark:bg-zinc-800 text-zinc-550 dark:text-zinc-400 rounded-lg">
            {!question ? "Tự luận" : qType === "essay" ? "Tự luận" : "Trắc nghiệm"}
          </span>
        </div>

        {!question ? (
          <div className="space-y-6">
            <div className="space-y-3">
              {essayQuestions.map((q, idx) => {
                const originalIndex = quiz.questions.findIndex((originalQ) => originalQ === q);
                return (
                  <div key={idx} className="p-4 bg-zinc-50 dark:bg-zinc-950/20 border border-zinc-200 dark:border-zinc-800 rounded-2xl space-y-1">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide">
                      Câu hỏi tự luận {idx + 1} (Câu {originalIndex + 1} trong đề)
                    </span>
                    <p className="text-sm font-extrabold text-zinc-850 dark:text-zinc-100 leading-relaxed">
                      {q.question_text}
                    </p>
                  </div>
                );
              })}
            </div>

            <div className="space-y-4">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                className="hidden"
              />

              <div
                onClick={triggerFileInput}
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center space-y-3 ${
                  essayFilePath
                    ? "border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/5"
                    : "border-zinc-300 dark:border-zinc-700 hover:border-violet-500 dark:hover:border-violet-400 bg-zinc-50/50 dark:bg-zinc-950/20"
                }`}
              >
                {uploadingEssay ? (
                  <div className="flex flex-col items-center space-y-2">
                    <Loader2 className="w-10 h-10 text-violet-600 animate-spin" />
                    <p className="text-xs font-bold text-zinc-555">Đang tải và xử lý file bài làm...</p>
                  </div>
                ) : essayFilePath ? (
                  <div className="flex flex-col items-center space-y-2 animate-fadeIn">
                    <div className="p-3 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full">
                      <CheckCircle2 className="w-8 h-8" />
                    </div>
                    <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">Đã nộp tệp bài làm!</p>
                    <p className="text-[11px] text-zinc-500 font-semibold max-w-xs truncate">
                      {essayFilePath.split(/[\\/]/).pop()}
                    </p>
                    <button
                      type="button"
                      className="mt-2 text-xs font-bold text-violet-600 hover:underline cursor-pointer"
                    >
                      Chọn tệp khác để thay thế
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="p-3 bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-650 rounded-full">
                      <UploadCloud className="w-8 h-8" />
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-bold text-zinc-750 dark:text-zinc-300">
                        Click để chọn hoặc kéo thả tệp bài làm tự luận
                      </p>
                      <p className="text-[10px] text-zinc-400 font-medium">
                        Hỗ trợ ảnh viết tay (.png, .jpg), PDF, Word (.docx) hoặc TXT
                      </p>
                    </div>
                  </>
                )}
              </div>

              <div className="p-4 bg-violet-50/30 dark:bg-violet-950/10 border border-violet-100/30 dark:border-violet-900/20 rounded-xl">
                <p className="text-xs text-zinc-550 dark:text-zinc-400 font-medium leading-relaxed">
                  💡 <span className="font-bold text-violet-600">Lưu ý quan trọng:</span> Bạn chỉ cần tải lên **01 tệp duy nhất** chứa toàn bộ lời giải/bài viết của tất cả các câu hỏi tự luận trong đề thi này. AI Grader sẽ tự động trích xuất OCR và chấm chi tiết từng câu.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <>
            <h3 className="text-base font-extrabold text-zinc-850 dark:text-zinc-100 leading-relaxed mb-6">
              <MathRenderer content={question.question_text || ""} />
            </h3>

            {qType === "essay" ? (
              <div className="space-y-6">
                {!isReview ? (
                  <div className="space-y-4">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileChange}
                      accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                      className="hidden"
                    />

                    <div
                      onClick={triggerFileInput}
                      className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center space-y-3 ${
                        essayFilePath
                          ? "border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/5"
                          : "border-zinc-300 dark:border-zinc-700 hover:border-violet-500 dark:hover:border-violet-400 bg-zinc-50/50 dark:bg-zinc-950/20"
                      }`}
                    >
                      {uploadingEssay ? (
                        <div className="flex flex-col items-center space-y-2">
                          <Loader2 className="w-10 h-10 text-violet-600 animate-spin" />
                          <p className="text-xs font-bold text-zinc-555">Đang tải và xử lý file bài làm...</p>
                        </div>
                      ) : essayFilePath ? (
                        <div className="flex flex-col items-center space-y-2 animate-fadeIn">
                          <div className="p-3 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-655 text-white rounded-full">
                            <CheckCircle2 className="w-8 h-8" />
                          </div>
                          <p className="text-sm font-bold text-emerald-600">Đã nộp tệp bài làm!</p>
                        </div>
                      ) : (
                        <p>Tải tệp tự luận</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6 animate-fadeIn">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-5 border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 rounded-2xl flex flex-col justify-between">
                        <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide">
                          Bài làm của bạn (Trích xuất OCR)
                        </span>
                        <p className="mt-3 text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed font-semibold max-h-[140px] overflow-y-auto whitespace-pre-wrap">
                          {attemptAnswer?.answer || "[Không có dữ liệu bài làm]"}
                        </p>
                      </div>

                      <div className={`p-5 border rounded-2xl flex flex-col justify-between ${
                        (attemptAnswer?.score ?? 0) >= 5.0
                          ? "border-emerald-100 bg-emerald-50/10 dark:bg-emerald-950/5"
                          : "border-red-100 bg-red-50/10 dark:bg-red-950/5"
                      }`}>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide">
                            Điểm số tự luận
                          </span>
                          <span className={`px-2.5 py-1 text-xs font-bold rounded-lg ${
                            (attemptAnswer?.score ?? 0) >= 5.0
                              ? "bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400"
                              : "bg-red-100 text-red-655 dark:bg-red-900/30 dark:text-red-400"
                          }`}>
                            {attemptAnswer?.score !== undefined ? `${attemptAnswer.score} / 10` : "Chưa chấm"}
                          </span>
                        </div>

                        <div className="mt-3 space-y-2">
                          <div className="flex items-center gap-1 text-[10px] font-bold text-violet-600 uppercase">
                            <Sparkles className="w-3.5 h-3.5" />
                            Lời phê từ AI Grader
                          </div>
                          <p className="text-xs text-zinc-655 dark:text-zinc-400 leading-relaxed font-semibold italic">
                            "{attemptAnswer?.feedback || "Không có lời phê nhận xét."}"
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="p-5 bg-indigo-50/20 dark:bg-zinc-950/20 border border-indigo-100/30 dark:border-zinc-800 rounded-xl space-y-2">
                      <h4 className="text-xs font-bold text-indigo-650 dark:text-indigo-400 uppercase tracking-wider">
                        Gợi ý đáp án / Bài mẫu gợi ý
                      </h4>
                      <p className="text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed font-semibold whitespace-pre-wrap">
                        <MathRenderer content={question.correct_answer || ""} />
                      </p>
                    </div>

                    {question.explanation && (
                      <div className="p-4 bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200 dark:border-zinc-800 rounded-xl space-y-1">
                        <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wide">
                          Tiêu chí chấm điểm
                        </span>
                        <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                          <MathRenderer content={question.explanation || ""} />
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {question.options?.map((opt) => {
                  const isSelected = selectedAnswers[questionIndex] === opt.key;
                  const isCorrect = question.correct_answer === opt.key;
                  const optionStyle = getOptionStyle(isReview, isSelected, isCorrect);

                  return (
                    <button
                      key={opt.key}
                      onClick={() => onSelectOption(questionIndex, opt.key)}
                      disabled={isReview}
                      className={`w-full flex items-start gap-4 p-4 border rounded-xl text-left transition-all ${optionStyle}`}
                    >
                      <span className="font-extrabold text-sm">{opt.key}.</span>
                      <span className="text-sm font-semibold">
                        <MathRenderer content={opt.value || ""} />
                      </span>
                    </button>
                  );
                })}

                {isReview && question.explanation && (
                  <div className="mt-8 p-5 bg-indigo-50/30 dark:bg-zinc-950/30 border border-indigo-100/50 dark:border-zinc-800 rounded-xl space-y-2">
                    <h4 className="text-xs font-bold text-indigo-650 dark:text-indigo-400 uppercase tracking-wider">
                      Giải thích đáp án AI
                    </h4>
                    <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                      <MathRenderer content={question.explanation || ""} />
                    </p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-zinc-100 dark:border-zinc-800 mt-8">
        <button
          onClick={onPrevious}
          disabled={questionIndex === 0}
          className="px-4 py-2 border border-zinc-200 dark:border-zinc-700 disabled:opacity-30 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4" />
          Câu trước
        </button>

        {questionIndex < totalPages - 1 ? (
          <button
            onClick={onNext}
            className="px-4 py-2 bg-zinc-800 dark:bg-zinc-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
          >
            Câu sau
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : !isReview ? (
          <button
            onClick={onSubmit}
            disabled={submitting}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-md shadow-indigo-500/10"
          >
            <Send className="w-3.5 h-3.5" />
            Nộp bài thi
          </button>
        ) : (
          <button
            onClick={onBackToList}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Quay lại kho
          </button>
        )}
      </div>
    </div>
  );
}
