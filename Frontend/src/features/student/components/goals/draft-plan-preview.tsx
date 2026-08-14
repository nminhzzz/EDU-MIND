"use client";

import React, { useState } from "react";
import { LayoutGrid, Calendar, BookOpen, CheckCircle2 } from "lucide-react";
import { Badge, Card, TabButton, TabsList } from "@/components/ui";
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
    <Card className="w-full space-y-7 p-5 sm:p-7">
      {/* Header Info */}
      <div className="flex flex-col justify-between gap-5 border-b border-zinc-100 pb-6 dark:border-zinc-800 sm:flex-row sm:items-center">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge className="border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-300">
              Bản thảo Lộ trình AI
            </Badge>
          </div>
          <h2 className="flex items-center gap-2 text-xl font-bold tracking-tight text-zinc-950 dark:text-white sm:text-2xl">
            Lộ trình học tập đề xuất
          </h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            <span className="font-semibold text-zinc-800 dark:text-zinc-200">{subjectObj?.name || "Môn học"}</span><span className="mx-2 text-zinc-300">•</span>Mục tiêu <span className="font-semibold text-indigo-600">{targetScore}/10</span><span className="mx-2 text-zinc-300">•</span>Hạn {deadline}
          </p>
        </div>

        {/* View Mode Switcher */}
        <TabsList className="self-start sm:self-auto">
          <TabButton
            type="button"
            onClick={() => setViewMode("daily")}
            active={viewMode === "daily"}
            className="flex items-center gap-1.5"
          >
            <LayoutGrid className="w-3.5 h-3.5" /> Chi tiết theo ngày
          </TabButton>
          <TabButton
            type="button"
            onClick={() => setViewMode("timeline")}
            active={viewMode === "timeline"}
            className="flex items-center gap-1.5"
          >
            <Calendar className="w-3.5 h-3.5" /> Theo tuần
          </TabButton>
        </TabsList>
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
                  className="p-4 border border-zinc-200/70 dark:border-zinc-800 rounded-md bg-zinc-50/60 dark:bg-zinc-950/40 space-y-1.5"
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
    </Card>
  );
}
