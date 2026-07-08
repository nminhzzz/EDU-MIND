"use client";

import React from "react";
import { QuickQuizPane } from "@/features/student/components/quizzes/quick-quiz-pane";
import type { StudyPlan } from "@/features/student/types";
import { useTaskStudy } from "@/features/student/hooks/use-task-study";
import { TaskMaterialPane } from "./task-material-pane";
import { TaskStudyFooter } from "./task-study-footer";
import { TaskStudyHeader } from "./task-study-header";
import { TaskStudyTabs } from "./task-study-tabs";
import { TaskTutorPane } from "./task-tutor-pane";

interface TaskStudyViewProps {
  task: StudyPlan;
  backHref: string;
  onRefresh?: () => void;
}

export function TaskStudyView({ task, backHref, onRefresh }: TaskStudyViewProps) {
  const { activeTab, setActiveTab, subjectId, handleQuizSuccess } = useTaskStudy(
    task,
    onRefresh,
  );

  return (
    <div className="flex flex-col min-h-[calc(100vh-8rem)] border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden bg-white dark:bg-zinc-900 shadow-sm">
      <TaskStudyHeader title={task.title} backHref={backHref} />

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 min-h-0">
        <div className="border-b lg:border-b-0 lg:border-r border-zinc-200 dark:border-zinc-800 flex flex-col min-h-[420px] lg:min-h-0 overflow-hidden">
          <TaskStudyTabs activeTab={activeTab} onTabChange={setActiveTab} />

          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === "material" ? (
              <TaskMaterialPane task={task} />
            ) : (
              <div className="h-full">
                <QuickQuizPane
                  studyPlanId={task.id}
                  subjectId={subjectId}
                  topic={task.title}
                  onSuccess={handleQuizSuccess}
                />
              </div>
            )}
          </div>
        </div>

        <TaskTutorPane subjectId={subjectId} topic={task.title} />
      </div>

      <TaskStudyFooter task={task} backHref={backHref} />
    </div>
  );
}
