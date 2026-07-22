"use client";

import React from "react";
import { useParams } from "next/navigation";
import { GoalDetailView } from "@/features/student/components/goals";

export default function StudentGoalDetailPage() {
  const params = useParams();
  const rawId = params?.id;
  const goalId = Number(rawId);

  if (!goalId || isNaN(goalId)) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center">
        <p className="text-sm font-semibold text-red-500">Mã lộ trình học không hợp lệ.</p>
      </div>
    );
  }

  return <GoalDetailView goalId={goalId} />;
}
