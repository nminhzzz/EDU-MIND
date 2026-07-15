"use client";

import React, { useEffect } from "react";
import { QuickQuizPane } from "@/features/student/components/quizzes/quick-quiz-pane";
import type { StudyPlan } from "@/features/student/types";
import { useTaskStudy } from "@/features/student/hooks/use-task-study";
import { TaskMaterialPane } from "./task-material-pane";
import { TaskStudyFooter } from "./task-study-footer";
import { TaskStudyHeader } from "./task-study-header";
import { TaskStudyTabs } from "./task-study-tabs";
import { TaskTutorPane } from "./task-tutor-pane";
import { Sparkles } from "lucide-react";

interface TaskStudyViewProps {
  task: StudyPlan;
  backHref: string;
  onRefresh?: (silent?: boolean) => void;
}

export function TaskStudyView({ task, backHref, onRefresh }: TaskStudyViewProps) {
  const { activeTab, setActiveTab, subjectId, handleQuizSuccess } = useTaskStudy(
    task,
    onRefresh,
  );

  // Tự động tải lại thông tin nhiệm vụ nếu chưa có tài liệu lý thuyết (AI đang sinh ngầm ở background)
  useEffect(() => {
    if (task.rag_content) return;

    const interval = setInterval(() => {
      if (onRefresh) {
        onRefresh(true); // Gọi silent refresh (không hiện màn hình loading chính)
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [task.rag_content, onRefresh]);

  // Nếu bài học do AI sinh và tài liệu lý thuyết chưa hoàn thành
  if (task.ai_generated && !task.rag_content) {
    return (
      <div className="flex flex-col min-h-[calc(100vh-8rem)] border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden bg-white dark:bg-zinc-900 shadow-sm">
        <TaskStudyHeader title={task.title} backHref={backHref} />
        
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-zinc-50/50 dark:bg-zinc-950/10 space-y-6">
          <div className="relative">
            <div className="w-16 h-16 rounded-full border-4 border-indigo-100 dark:border-indigo-950 border-t-indigo-600 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-indigo-600 animate-pulse" />
            </div>
          </div>
          
          <div className="space-y-2 max-w-md">
            <h3 className="text-base font-extrabold text-zinc-800 dark:text-zinc-150">
              AI đang chuẩn bị nội dung bài học...
            </h3>
            <p className="text-[11px] text-zinc-400 dark:text-zinc-500 leading-relaxed font-semibold">
              Hệ thống đang tự động soạn thảo bài giảng lý thuyết chi tiết và thiết kế đề kiểm tra nhanh cho chủ đề này.
              Quá trình này thường mất từ 30–60 giây. Bài học sẽ tự động mở ra ngay khi hoàn tất!
            </p>
          </div>

          <div className="pt-2">
            <a
              href={backHref}
              className="px-4 py-2.5 border border-zinc-200 dark:border-zinc-850 bg-white dark:bg-zinc-900 hover:bg-zinc-50 dark:hover:bg-zinc-800/80 rounded-xl text-xs font-bold text-zinc-600 dark:text-zinc-350 shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Quay lại danh sách nhiệm vụ
            </a>
          </div>
        </div>
      </div>
    );
  }

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
