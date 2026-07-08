"use client";

import React from "react";
import { motion } from "framer-motion";
import { Plus, Sparkles } from "lucide-react";
import type { StudyGoalResponse, Subject } from "@/features/student/types";
import { GoalCard } from "./goal-card";

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
    <motion.div
      key="list_goals"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-6 text-left"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-br from-white to-indigo-50/30 dark:from-zinc-900 dark:to-indigo-950/20 border border-zinc-200/80 dark:border-zinc-800 p-6 sm:p-8 rounded-2xl shadow-sm">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
              Lộ trình học tập của bạn
            </h1>
            <Sparkles className="w-5 h-5 text-indigo-500" />
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-xl">
            Quản lý các lộ trình học tập do AI lập riêng cho bạn.
          </p>
        </div>
        <button
          type="button"
          onClick={onCreateClick}
          className="shrink-0 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl shadow-md shadow-indigo-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Tạo lộ trình mới
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5 auto-rows-fr">
        {goals.map((goal) => (
          <GoalCard
            key={goal.id}
            goal={goal}
            subject={subjects.find((s) => s.id === goal.subject_id)}
            goalsLoading={goalsLoading}
            onDelete={onDeleteGoal}
          />
        ))}
      </div>
    </motion.div>
  );
}
