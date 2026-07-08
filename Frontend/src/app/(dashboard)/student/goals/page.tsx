"use client";

import React from "react";
import { GoalsWizard } from "@/features/student/components/goals/goals-wizard";
import { useGoalsWizard } from "@/features/student/hooks/use-goals-wizard";

export default function GoalsPage() {
  const wizard = useGoalsWizard();

  return <GoalsWizard wizard={wizard} />;
}
