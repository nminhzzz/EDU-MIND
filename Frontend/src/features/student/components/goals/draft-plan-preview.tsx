"use client";

import React from "react";
import type { DraftResponse, Subject } from "@/features/student/types";

interface DraftPlanPreviewProps {
  draft: DraftResponse;
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
}

export function DraftPlanPreview({
  draft,
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
}: DraftPlanPreviewProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm">
      <div className="pb-4 border-b border-zinc-200 dark:border-zinc-850 mb-6">
        <h2 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
          Bản thảo lộ trình học đề xuất từ AI Agent
        </h2>
        <p className="text-[10px] text-zinc-500 font-mono mt-1 uppercase">
          Môn: {subjects.find((s) => String(s.id) === selectedSubjectId)?.name} // Điểm mong muốn: {targetScore} // Hạn chót: {deadline}
        </p>
      </div>

      <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
        <div className="space-y-4 text-left">
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">
            📅 Lộ trình theo tuần
          </h3>
          {draft.plan.weeks.map((week) => (
            <div
              key={week.week}
              className="relative pl-6 border-l border-zinc-200 dark:border-zinc-800 space-y-2"
            >
              <span className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-indigo-600 border border-white dark:border-zinc-900" />
              <h4 className="text-xs font-bold text-zinc-850 dark:text-zinc-200">
                Tuần {week.week}
              </h4>
              <div className="space-y-1 pl-2">
                {week.tasks.map((task, idx) => (
                  <p key={idx} className="text-xs font-semibold text-zinc-550 dark:text-zinc-450">
                    • {task}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>

        {draft.plan.daily_schedule && draft.plan.daily_schedule.length > 0 && (
          <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-4 text-left">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">
              ⏰ Thời khóa biểu hàng ngày chi tiết
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {draft.plan.daily_schedule.map((day, idx) => (
                <div
                  key={idx}
                  className="bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/50 dark:border-zinc-850 p-4 rounded-xl space-y-2 shadow-sm animate-fade-in"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md font-mono">
                      {day.date}
                    </span>
                    <span className="text-[9px] text-zinc-400 dark:text-zinc-550 font-bold">
                      {day.start_time} - {day.end_time}
                    </span>
                  </div>
                  <h5 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200">{day.task}</h5>
                  <p className="text-[10px] text-zinc-550 dark:text-zinc-450 leading-relaxed font-semibold">
                    {day.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {draft.plan.curriculum_materials && draft.plan.curriculum_materials.length > 0 && (
          <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-3 text-left">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">
              📚 Tài liệu bài giảng RAG tham khảo
            </h3>
            <div className="space-y-2.5">
              {draft.plan.curriculum_materials.map((mat, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-zinc-150 dark:border-zinc-800 rounded-xl bg-zinc-50/30 dark:bg-zinc-900/10"
                >
                  <h5 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200">{mat.topic}</h5>
                  <p className="text-[10px] text-zinc-550 dark:text-zinc-400 mt-1 leading-relaxed font-semibold">
                    {mat.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {draft.plan.quizzes && draft.plan.quizzes.length > 0 && (
          <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-3 text-left">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">
              📝 Đề thi luyện tập AI sinh kèm
            </h3>
            <div className="space-y-2.5">
              {draft.plan.quizzes.map((quiz, idx) => (
                <div
                  key={idx}
                  className="p-3 border border-zinc-150 dark:border-zinc-800 rounded-xl bg-zinc-50/30 dark:bg-zinc-900/10 flex justify-between items-center"
                >
                  <div>
                    <h5 className="text-xs font-extrabold text-zinc-850 dark:text-zinc-200">{quiz.title}</h5>
                    <span className="text-[10px] text-zinc-400 font-bold">
                      {quiz.questions ? quiz.questions.length : 0} câu hỏi trắc nghiệm
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
