"use client";

import React, { useState } from "react";
import { LayoutGrid, Calendar, BookOpen, Sparkles, CheckCircle2 } from "lucide-react";
import type { DraftResponse, Subject } from "@/features/student/types";
import { DraftKpiWidgets } from "./draft-kpi-widgets";
import { DraftTimelineView } from "./draft-timeline-view";
import { DraftDailyGridView } from "./draft-daily-grid-view";

interface DraftPlanPreviewProps {
  draft: DraftResponse;
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
  onUpdatePlan: (updatedPlan: DraftResponse["plan"]) => void;
}

export function DraftPlanPreview({
  draft,
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
  onUpdatePlan,
}: DraftPlanPreviewProps) {
  const [viewMode, setViewMode] = useState<"timeline" | "daily">("daily");
  const subjectObj = subjects.find((s) => String(s.id) === String(selectedSubjectId));

  return (
    <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/80 dark:border-zinc-800 p-6 sm:p-8 rounded-3xl shadow-sm space-y-6 w-full">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-zinc-200/60 dark:border-zinc-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-black uppercase tracking-wider bg-violet-100 dark:bg-violet-950/60 text-violet-700 dark:text-violet-300 px-2.5 py-0.5 rounded-full border border-violet-200/50 dark:border-violet-800/50">
              Bản thảo Lộ trình AI
            </span>
          </div>
          <h2 className="font-extrabold text-lg sm:text-xl tracking-tight text-zinc-900 dark:text-white flex items-center gap-2">
            Lộ trình Học tập & Thời khóa biểu Đề xuất
          </h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
            Môn học: <span className="text-violet-600 dark:text-violet-400 font-bold">{subjectObj?.name || "Môn học"}</span> // Mục tiêu: <span className="font-mono text-violet-600 dark:text-violet-400 font-bold">{targetScore}/10</span> // Hạn chót: <span className="font-mono text-zinc-700 dark:text-zinc-300 font-bold">{deadline}</span>
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1 bg-zinc-100 dark:bg-zinc-950 p-1 rounded-2xl border border-zinc-200/80 dark:border-zinc-800 self-start sm:self-auto shrink-0 shadow-2xs">
          <button
            type="button"
            onClick={() => setViewMode("daily")}
            className={`px-3.5 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer flex items-center gap-1.5 ${
              viewMode === "daily"
                ? "bg-white dark:bg-zinc-800 text-violet-600 dark:text-violet-400 shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" /> Chi tiết theo ngày
          </button>
          <button
            type="button"
            onClick={() => setViewMode("timeline")}
            className={`px-3.5 py-2 rounded-xl text-xs font-extrabold transition-all cursor-pointer flex items-center gap-1.5 ${
              viewMode === "timeline"
                ? "bg-white dark:bg-zinc-800 text-violet-600 dark:text-violet-400 shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" /> Theo tuần
          </button>
        </div>
      </div>

      {/* KPI Widgets */}
      <DraftKpiWidgets plan={draft.plan} targetScore={targetScore} />

      {/* Main Schedule Container */}
      <div className="w-full">
        {viewMode === "timeline" ? (
          <DraftTimelineView plan={draft.plan} onUpdatePlan={onUpdatePlan} />
        ) : (
          <DraftDailyGridView plan={draft.plan} onUpdatePlan={onUpdatePlan} />
        )}

        {/* RAG Context Materials */}
        {draft.plan.curriculum_materials && draft.plan.curriculum_materials.length > 0 && (
          <div className="mt-8 pt-6 border-t border-zinc-200/60 dark:border-zinc-800 space-y-3 text-left">
            <h4 className="text-xs font-black text-zinc-500 dark:text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-violet-500" /> Tài liệu RAG & Giáo trình đã tham chiếu
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {draft.plan.curriculum_materials.map((mat, idx) => (
                <div
                  key={idx}
                  className="p-4 border border-zinc-200/70 dark:border-zinc-800 rounded-2xl bg-zinc-50/60 dark:bg-zinc-950/40 space-y-1.5"
                >
                  <h5 className="text-xs font-black text-zinc-800 dark:text-zinc-200 flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                    {mat.topic}
                  </h5>
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
                    {mat.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
