"use client";

import React from "react";
import { Plus } from "lucide-react";
import type { StudyGoalResponse, Subject } from "@/features/student/types";
import { GoalCard } from "./goal-card";
import { Button, EmptyState, PageHeader, Skeleton } from "@/components/ui";

interface GoalsListStepProps {
  goals: StudyGoalResponse[];
  subjects: Subject[];
  goalsLoading: boolean;
  onCreateClick: () => void;
  onDeleteGoal: (id: number) => void;
}

export function GoalsListStep({
  goals,
  subjects,
  goalsLoading,
  onCreateClick,
  onDeleteGoal,
}: GoalsListStepProps) {
  return (
    <div className="space-y-6 text-left">
      <PageHeader eyebrow="AI Study Planner" title="Lộ trình học tập" description="Quản lý các lộ trình cá nhân hóa theo mục tiêu và thời gian của bạn." actions={<Button onClick={onCreateClick}><Plus className="size-4" /> Tạo lộ trình mới</Button>} />

      {goalsLoading ? (
        <div className="grid gap-5 md:grid-cols-2">{[0, 1, 2, 3].map((item) => <Skeleton key={item} className="h-52" />)}</div>
      ) : goals.length === 0 ? (
        <EmptyState title="Bạn chưa có lộ trình học" description="Tạo lộ trình đầu tiên để AI xây dựng kế hoạch học theo lịch rảnh của bạn." actionLabel="Tạo lộ trình" onAction={onCreateClick} />
      ) : <div className="grid grid-cols-1 md:grid-cols-2 gap-5 auto-rows-fr">
        {goals.map((goal) => (
          <GoalCard
            key={goal.id}
            goal={goal}
            subject={subjects.find((s) => s.id === goal.subject_id)}
            goalsLoading={goalsLoading}
            onDelete={onDeleteGoal}
          />
        ))}
      </div>}
    </div>
  );
}
