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
  onRetryWrong?: () => void;
}

export function AIQuizFeedbackCard({
  assessment,
  score,
  correctCount,
  totalQuestions,
  onRetryWrong,
}: AIQuizFeedbackCardProps) {
  if (!assessment && score === undefined) return null;

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
    <div className="p-6 rounded-2xl bg-gradient-to-br from-violet-500/10 via-purple-500/10 to-indigo-500/10 border border-violet-200 dark:border-violet-900/40 shadow-lg space-y-5 text-left animate-fadeIn">
      {/* Header with AI Tutor Avatar */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-violet-500/30 shrink-0">
          <BrainCircuit className="w-6 h-6 animate-pulse" />
        </div>
        <div className="space-y-1 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black uppercase tracking-wider text-violet-600 dark:text-violet-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              Đánh giá & Lời phê từ AI Tutor
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold bg-violet-100 dark:bg-violet-950/60 text-violet-700 dark:text-violet-300 rounded-md">
              {score.toFixed(1)} / 10 Điểm
            </span>
          </div>
          <p className="text-sm font-bold text-zinc-900 dark:text-zinc-100 leading-relaxed italic">
            "{overall}"
          </p>
        </div>
      </div>

      {/* Grid Strengths vs Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
        {/* Strengths */}
        <div className="p-4 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40 space-y-2">
          <h4 className="text-xs font-black uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            Điểm mạnh đã nắm vững ({correctCount}/{totalQuestions} câu):
          </h4>
          {strengths.length > 0 ? (
            <ul className="space-y-1 pl-1">
              {strengths.map((item, idx) => (
                <li key={idx} className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 flex items-start gap-1.5">
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
        <div className="p-4 rounded-xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 space-y-2">
          <h4 className="text-xs font-black uppercase tracking-wider text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            Lỗ hổng kiến thức cần ôn lại ({totalQuestions - correctCount} câu):
          </h4>
          {weaknesses.length > 0 ? (
            <ul className="space-y-1 pl-1">
              {weaknesses.map((item, idx) => (
                <li key={idx} className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 flex items-start gap-1.5">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-emerald-600 font-bold">Tuyệt vời! Bạn không để hổng kiến thức nào.</p>
          )}
        </div>
      </div>

      {/* Recommendation & Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-violet-100 dark:border-violet-900/30">
        <div className="flex items-center gap-2 text-xs font-semibold text-zinc-650 dark:text-zinc-350">
          <ArrowRight className="w-4 h-4 text-violet-600 shrink-0" />
          <span><strong className="text-violet-600 dark:text-violet-400">Gợi ý AI:</strong> {recommendation}</span>
        </div>

        {onRetryWrong && totalQuestions - correctCount > 0 && (
          <button
            type="button"
            onClick={onRetryWrong}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Luyện lại các câu sai
          </button>
        )}
      </div>
    </div>
  );
}
