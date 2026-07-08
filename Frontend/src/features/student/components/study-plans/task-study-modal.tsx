"use client";

import React from "react";
import { QuickQuizPane } from "@/features/student/components/quizzes/quick-quiz-pane";
import type { StudyPlan } from "@/features/student/types";
import { StudentModal } from "@/features/student/components/common/student-modal";
import { useTaskStudy } from "@/features/student/hooks/use-task-study";
import { TaskMaterialPane } from "./task-material-pane";
import { TaskStudyFooter } from "./task-study-footer";
import { TaskStudyHeader } from "./task-study-header";
import { TaskStudyTabs } from "./task-study-tabs";
import { TaskTutorPane } from "./task-tutor-pane";

export interface TaskStudyModalProps {
  task: StudyPlan;
  onClose: () => void;
  onToggleStatus?: (task: StudyPlan) => Promise<void>;
  onRefresh?: () => void;
}

export function TaskStudyModal({
  task,
  onClose,
  onRefresh,
}: TaskStudyModalProps) {
  const { activeTab, setActiveTab, subjectId, handleQuizSuccess } = useTaskStudy(
    task,
    onRefresh,
  );

  return (
    <StudentModal
      isOpen
      onClose={onClose}
      maxWidth="5xl"
      overlayZIndex="z-40"
      withAnimatePresence={false}
      showCloseButton={false}
      contentClassName="h-[85vh] flex flex-col overflow-hidden"
      animation={{ scale: 0.96, y: 15 }}
    >
      <TaskStudyHeader title={task.title} onClose={onClose} />

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 overflow-hidden">
        <div className="border-r border-zinc-200 dark:border-zinc-800 flex flex-col h-full overflow-hidden">
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

      <TaskStudyFooter task={task} onClose={onClose} />
    </StudentModal>
  );
}
