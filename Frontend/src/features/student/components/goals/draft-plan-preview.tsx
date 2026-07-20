"use client";

import React, { useState } from "react";
import { LayoutGrid, Calendar, BookOpen } from "lucide-react";
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
  const [viewMode, setViewMode] = useState<"timeline" | "daily">("daily"); // Default to daily detailed view
  const subjectObj = subjects.find((s) => String(s.id) === String(selectedSubjectId));

  return (
    <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-md border border-zinc-200/80 dark:border-zinc-800 p-6 sm:p-8 rounded-3xl shadow-sm space-y-6 w-full">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-200/60 dark:border-zinc-850">
        <div>
          <h2 className="font-black text-lg tracking-tight text-zinc-900 dark:text-white uppercase">
            3. Bản thảo Lộ trình Học tập do AI Đề xuất (Có thể Chỉnh sửa)
          </h2>
          <p className="text-xs text-zinc-400 font-semibold mt-1">
            Môn: <span className="text-indigo-600 dark:text-indigo-400 font-bold">{subjectObj?.name || "Môn học"}</span> // Điểm mong muốn: <span className="font-mono text-indigo-600 font-bold">{targetScore}</span> // Hạn chót: <span className="font-mono text-zinc-600 dark:text-zinc-300 font-bold">{deadline}</span>
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1 bg-zinc-100 dark:bg-zinc-950 p-1 rounded-2xl border border-zinc-200/60 dark:border-zinc-800 self-start sm:self-auto shrink-0">
          <button
            type="button"
            onClick={() => setViewMode("daily")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              viewMode === "daily"
                ? "bg-white dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 shadow-sm"
                : "text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" /> ⏰ Thời Khóa Biểu Chi Tiết (1 Ngày/Hàng)
          </button>
          <button
            type="button"
            onClick={() => setViewMode("timeline")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              viewMode === "timeline"
                ? "bg-white dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 shadow-sm"
                : "text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" /> 📊 Timeline Theo Tuần
          </button>
        </div>
      </div>

      {/* KPI Widgets */}
      <DraftKpiWidgets plan={draft.plan} targetScore={targetScore} />

      {/* Full-width Natural Plan View Container (No scroll restrictions) */}
      <div className="w-full">
        {viewMode === "timeline" ? (
          <DraftTimelineView plan={draft.plan} onUpdatePlan={onUpdatePlan} />
        ) : (
          <DraftDailyGridView plan={draft.plan} onUpdatePlan={onUpdatePlan} />
        )}

        {/* RAG Context Materials if available */}
        {draft.plan.curriculum_materials && draft.plan.curriculum_materials.length > 0 && (
          <div className="mt-8 pt-6 border-t border-zinc-200/60 dark:border-zinc-850 space-y-3 text-left">
            <h4 className="text-xs font-black text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-indigo-500" /> Giáo trình & Tài liệu tham khảo RAG
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {draft.plan.curriculum_materials.map((mat, idx) => (
                <div
                  key={idx}
                  className="p-4 border border-zinc-200/60 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-950/30"
                >
                  <h5 className="text-xs font-black text-zinc-800 dark:text-zinc-200">{mat.topic}</h5>
                  <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1 leading-relaxed font-medium">
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
