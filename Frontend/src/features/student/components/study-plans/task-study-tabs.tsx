"use client";

import React from "react";
import { TaskStudyTab } from "@/features/student/hooks/use-task-study";

interface TaskStudyTabsProps {
  activeTab: TaskStudyTab;
  onTabChange: (tab: TaskStudyTab) => void;
}

export function TaskStudyTabs({ activeTab, onTabChange }: TaskStudyTabsProps) {
  return (
    <div className="flex border-b border-zinc-200 dark:border-zinc-800">
      <button
        onClick={() => onTabChange("material")}
        className={`flex-1 py-3 text-xs font-bold transition-all border-b-2 cursor-pointer ${
          activeTab === "material"
            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
            : "border-transparent text-zinc-400 dark:text-zinc-500 hover:text-zinc-700"
        }`}
      >
        📖 Hướng dẫn học tập
      </button>
      <button
        onClick={() => onTabChange("quiz")}
        className={`flex-1 py-3 text-xs font-bold transition-all border-b-2 cursor-pointer ${
          activeTab === "quiz"
            ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
            : "border-transparent text-zinc-400 dark:text-zinc-500 hover:text-zinc-700"
        }`}
      >
        📝 Kiểm tra trắc nghiệm nhanh
      </button>
    </div>
  );
}
