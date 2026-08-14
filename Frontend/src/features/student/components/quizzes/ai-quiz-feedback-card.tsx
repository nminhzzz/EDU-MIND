"use client";

import React from "react";
import { Sparkles, CheckCircle2, AlertCircle, ArrowRight, RotateCcw, BrainCircuit } from "lucide-react";

export interface AIAssessmentData {
  overall_feedback: string;
  strengths?: string[];
  weaknesses?: string[];
  recommendation?: string;
}

interface AIQuizFeedbackCardProps {
  assessment?: AIAssessmentData | null;
  score: number;
  correctCount: number;
  totalQuestions: number;
  submittedAt?: string;
  onRetryWrong?: () => void;
}

export function AIQuizFeedbackCard({
  assessment,
  score,
  correctCount,
  totalQuestions,
  submittedAt,
  onRetryWrong,
}: AIQuizFeedbackCardProps) {
  if (!assessment && score === undefined) return null;

  // Backend trả submitted_at dạng UTC nhưng thiếu 'Z' → append 'Z' để JS parse đúng timezone
  const isRecentlySubmitted = submittedAt
    ? Date.now() - new Date(submittedAt.endsWith("Z") ? submittedAt : submittedAt + "Z").getTime() < 120_000
    : false;
  const isGenerating = !assessment && isRecentlySubmitted;

  const defaultFeedback =
    score >= 8.0
      ? "Xuất sắc! Bạn đã thể hiện tư duy làm bài tuyệt vời và nắm rất vững kiến thức."
      : score >= 5.0
      ? "Khá tốt! Bạn đã hoàn thành tốt các câu hỏi cơ bản, hãy rà soát lại các câu sai nhé."
      : "Đừng nản lòng! Hãy đọc lại lời giải chi tiết bên dưới để bổ sung lỗ hổng kiến thức.";

  const overall = assessment?.overall_feedback || defaultFeedback;
  const strengths = assessment?.strengths || (score >= 8.0 ? ["Nắm vững kiến thức trọng tâm bài học"] : []);
  const weaknesses = assessment?.weaknesses || (score < 8.0 ? ["Còn nhầm lẫn một số câu vận dụng"] : []);
  const recommendation = assessment?.recommendation || "Hãy xem lại giải thích chi tiết từng câu phía dưới.";

  return (
    <div className="p-6 sm:p-8 rounded-md bg-gradient-to-br from-sky-50 via-blue-50/70 to-cyan-50/40 dark:from-sky-950/70 dark:via-blue-950/40 dark:to-slate-900 border border-sky-200/80 dark:border-sky-900/50 shadow-xs space-y-6 text-left animate-fadeIn">
      {/* Header with AI Tutor Avatar */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-md bg-sky-600 dark:bg-sky-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20 shrink-0">
          <BrainCircuit className="w-6 h-6 animate-pulse" />
        </div>
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-black uppercase tracking-wider text-sky-700 dark:text-sky-300 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-sky-500" />
              Đánh giá & Lời phê từ AI Tutor
            </span>
            <span className="px-2.5 py-0.5 text-xs font-mono font-black bg-white dark:bg-sky-900 text-sky-800 dark:text-sky-100 border border-sky-200 dark:border-sky-800 rounded-md shadow-xs">
              {score.toFixed(1)} / 10 Điểm
            </span>
          </div>

          {isGenerating ? (
            <div className="space-y-1.5 pt-1">
              <p className="text-sm font-bold text-sky-700 dark:text-sky-300 flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-md bg-sky-500 animate-ping" />
                AI Tutor đang phân tích lỗ hổng kiến thức & tổng hợp lời phê...
              </p>
              <div className="w-full bg-sky-200/50 dark:bg-sky-950/50 h-1.5 rounded-md overflow-hidden">
                <div className="bg-gradient-to-r from-sky-400 to-blue-500 h-full w-2/3 animate-pulse rounded-md" />
              </div>
            </div>
          ) : (
            <p className="text-sm font-bold text-sky-950 dark:text-sky-100 leading-relaxed italic bg-white/70 dark:bg-sky-900/40 p-4 rounded-md border border-sky-100 dark:border-sky-800/60 shadow-xs">
              "{overall}"
            </p>
          )}
        </div>
      </div>

      {/* Grid Strengths vs Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
        {/* Strengths */}
        <div className="p-4 rounded-md bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200/80 dark:border-emerald-900/50 space-y-2.5">
          <h4 className="text-xs font-black uppercase tracking-wider text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            Điểm mạnh đã nắm vững ({correctCount}/{totalQuestions} câu):
          </h4>
          {strengths.length > 0 ? (
            <ul className="space-y-1.5 pl-1">
              {strengths.map((item, idx) => (
                <li key={idx} className="text-xs font-semibold text-emerald-950 dark:text-emerald-100 flex items-start gap-1.5">
                  <span className="text-emerald-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-zinc-500 italic">Cần cố gắng hơn ở các bài luyện tập sau.</p>
          )}
        </div>

        {/* Weaknesses */}
        <div className="p-4 rounded-md bg-amber-50/80 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900/50 space-y-2.5">
          <h4 className="text-xs font-black uppercase tracking-wider text-amber-800 dark:text-amber-300 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
            Lỗ hổng kiến thức cần ôn lại ({totalQuestions - correctCount} câu):
          </h4>
          {weaknesses.length > 0 ? (
            <ul className="space-y-1.5 pl-1">
              {weaknesses.map((item, idx) => (
                <li key={idx} className="text-xs font-semibold text-amber-950 dark:text-amber-100 flex items-start gap-1.5">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-emerald-700 dark:text-emerald-300 font-bold">Tuyệt vời! Bạn không để hổng kiến thức nào.</p>
          )}
        </div>
      </div>

      {/* Recommendation & Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-sky-200/60 dark:border-sky-900/50">
        <div className="flex items-center gap-2 text-xs font-semibold text-sky-900 dark:text-sky-200">
          <ArrowRight className="w-4 h-4 text-sky-600 dark:text-sky-400 shrink-0" />
          <span><strong className="text-sky-700 dark:text-sky-300">Gợi ý AI:</strong> {recommendation}</span>
        </div>

        {onRetryWrong && totalQuestions - correctCount > 0 && (
          <button
            type="button"
            onClick={onRetryWrong}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-md shadow-xs transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Luyện lại các câu sai
          </button>
        )}
      </div>
    </div>
  );
}
