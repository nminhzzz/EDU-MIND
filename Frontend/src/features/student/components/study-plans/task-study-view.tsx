"use client";

import React, { useEffect } from "react";
import { QuickQuizPane } from "@/features/student/components/quizzes/quick-quiz-pane";
import type { StudyPlan } from "@/features/student/types";
import { useTaskStudy } from "@/features/student/hooks/use-task-study";
import { TaskMaterialPane } from "./task-material-pane";
import { TaskStudyFooter } from "./task-study-footer";
import { TaskStudyHeader } from "./task-study-header";
import { TaskStudyTabs } from "./task-study-tabs";
import { Sparkles } from "lucide-react";
import { studyPlanApi } from "@/services/study-plan";

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

  // Start lazily only when the learner opens this task. The backend transition
  // and outbox unique key make this safe under React Strict Mode.
  useEffect(() => {
    if (!task.ai_generated || task.rag_content || task.lesson_status !== "not_started") return;
    void studyPlanApi
      .startGeneration(task.id)
      .then(() => onRefresh?.(true))
      .catch(() => undefined);
  }, [task.id, task.ai_generated, task.rag_content, task.lesson_status, onRefresh]);

  // Tự động tải lại thông tin nhiệm vụ nếu chưa có tài liệu lý thuyết (AI đang sinh ngầm ở background)
  useEffect(() => {
    if (
      task.rag_content ||
      task.lesson_status === "failed" ||
      task.lesson_status === "not_started"
    ) return;

    const interval = setInterval(() => {
      if (onRefresh) {
        onRefresh(true); // Gọi silent refresh (không hiện màn hình loading chính)
      }
    }, 6000);

    return () => clearInterval(interval);
  }, [task.rag_content, task.lesson_status, onRefresh]);

  // Nếu bài học do AI sinh và tài liệu lý thuyết chưa hoàn thành
  if (task.ai_generated && !task.rag_content) {
    const failed = task.lesson_status === "failed";
    return (
      <div className="flex flex-col min-h-[calc(100vh-8rem)] border border-zinc-200/80 dark:border-zinc-800 rounded-md overflow-hidden bg-white dark:bg-zinc-900 shadow-sm">
        <TaskStudyHeader title={task.title} backHref={backHref} />
        
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-zinc-50/50 dark:bg-zinc-950/10 space-y-6">
          <div className="relative">
            <div className="w-16 h-16 rounded-md border-4 border-indigo-100 dark:border-indigo-950 border-t-indigo-600 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-indigo-600 animate-pulse" />
            </div>
          </div>
          
          <div className="space-y-2 max-w-md">
            <h3 className="text-base font-extrabold text-zinc-800 dark:text-zinc-150">
              {failed ? "Không thể tạo nội dung bài học" : "AI đang chuẩn bị nội dung bài học..."}
            </h3>
            <p className="text-[11px] text-zinc-400 dark:text-zinc-500 leading-relaxed font-semibold">
              {failed
                ? "Dịch vụ AI gặp lỗi. Bạn có thể thử lại mà không tạo job trùng."
                : "Hệ thống đang soạn bài giảng và bài kiểm tra. Trang sẽ tự cập nhật khi hoàn tất."}
            </p>
            {failed && (
              <button
                type="button"
                onClick={async () => {
                  await studyPlanApi.retryGeneration(task.id);
                  onRefresh?.(true);
                }}
                className="mt-4 px-4 py-2 rounded-md bg-indigo-600 text-white text-xs font-bold"
              >
                Thử tạo lại
              </button>
            )}
          </div>

          <div className="pt-2">
            <a
              href={backHref}
              className="px-4 py-2.5 border border-zinc-200 dark:border-zinc-850 bg-white dark:bg-zinc-900 hover:bg-zinc-50 dark:hover:bg-zinc-800/80 rounded-md text-xs font-bold text-zinc-600 dark:text-zinc-350 shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Quay lại danh sách nhiệm vụ
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-[calc(100vh-8rem)] border border-zinc-200/80 dark:border-zinc-800 rounded-md overflow-hidden bg-white dark:bg-zinc-900 shadow-sm">
      <TaskStudyHeader title={task.title} backHref={backHref} />

      <div className="flex-1 flex flex-col min-h-0 w-full">
        <TaskStudyTabs activeTab={activeTab} onTabChange={setActiveTab} />

        <div className="flex-1 overflow-y-auto p-6 md:p-8 w-full">
          {activeTab === "material" ? (
            <TaskMaterialPane task={task} />
          ) : (
            <div className="h-full max-w-4xl mx-auto">
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

      <TaskStudyFooter task={task} backHref={backHref} />
    </div>
  );
}
