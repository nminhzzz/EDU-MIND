"use client";

import React from "react";
import { CheckCircle, HelpCircle, RefreshCw, Sparkles } from "lucide-react";
import { Badge, Button, PageHeader } from "@/components/ui";
import type { DraftResponse, Subject } from "@/features/student/types";
import { DraftPlanPreview } from "./draft-plan-preview";

interface GoalsDraftStepProps {
  draft: DraftResponse;
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
  loading: boolean;
  onConfirm: () => void;
  onCancelDraft: () => void;
  onUpdatePlan: (updatedPlan: DraftResponse["plan"]) => void;
}

export function GoalsDraftStep({ draft, subjects, selectedSubjectId, targetScore, deadline, loading, onConfirm, onCancelDraft, onUpdatePlan }: GoalsDraftStepProps) {
  return (
    <div className="mx-auto w-full max-w-6xl space-y-6">
      <PageHeader
        eyebrow="AI Study Planner"
        title="Kiểm tra lộ trình trước khi bắt đầu"
        description="Điều chỉnh tên bài học, nội dung và thời gian ngay bên dưới. Lộ trình chỉ được kích hoạt sau khi bạn xác nhận."
        actions={<Badge className="border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-300"><Sparkles className="size-3.5" /> Bản nháp có thể chỉnh sửa</Badge>}
      />

      <DraftPlanPreview draft={draft} subjects={subjects} selectedSubjectId={selectedSubjectId} targetScore={targetScore} deadline={deadline} onUpdatePlan={onUpdatePlan} />

      <div className="sticky bottom-3 z-20 flex flex-col gap-3 rounded-xl border border-zinc-200 bg-white/95 p-4 shadow-lg backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/95 sm:flex-row sm:items-center sm:justify-between">
        <span className="hidden items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400 md:flex"><HelpCircle className="size-4 text-indigo-500" /> Bạn vẫn có thể chỉnh sửa trước khi xác nhận.</span>
        <div className="ml-auto flex w-full items-center gap-2 sm:w-auto">
          <Button variant="secondary" className="flex-1 text-rose-600 sm:flex-none" onClick={onCancelDraft}><RefreshCw className="size-4" /> Hủy bản nháp</Button>
          <Button className="flex-1 bg-emerald-600 hover:bg-emerald-700 sm:flex-none" onClick={onConfirm} disabled={loading}><CheckCircle className="size-4" /> {loading ? "Đang kích hoạt..." : "Xác nhận và bắt đầu"}</Button>
        </div>
      </div>
    </div>
  );
}
