"use client";

import React from "react";
import type { DraftResponse, Subject } from "@/features/student/types";

interface DraftPlanPreviewProps {
  draft: DraftResponse;
  subjects: Subject[];
  selectedSubjectId: string;
  targetScore: number;
  deadline: string;
  onUpdatePlan: (updatedPlan: DraftResponse["plan"]) => void;
}

export function DraftPlanPreview({
  draft,
  subjects,
  selectedSubjectId,
  targetScore,
  deadline,
  onUpdatePlan,
}: DraftPlanPreviewProps) {
  // Update week task
  const handleWeekTaskChange = (weekIdx: number, taskIdx: number, val: string) => {
    const newWeeks = [...draft.plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks],
    };
    newWeeks[weekIdx].tasks[taskIdx] = val;
    onUpdatePlan({ ...draft.plan, weeks: newWeeks });
  };

  // Add week task
  const handleAddWeekTask = (weekIdx: number) => {
    const newWeeks = [...draft.plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks, "Nhiệm vụ tuần mới"],
    };
    onUpdatePlan({ ...draft.plan, weeks: newWeeks });
  };

  // Delete week task
  const handleDeleteWeekTask = (weekIdx: number, taskIdx: number) => {
    const newWeeks = [...draft.plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks],
    };
    newWeeks[weekIdx].tasks.splice(taskIdx, 1);
    onUpdatePlan({ ...draft.plan, weeks: newWeeks });
  };

  // Update daily schedule field
  const handleDailyScheduleFieldChange = (
    idx: number,
    field: "date" | "start_time" | "end_time" | "task" | "description",
    val: string
  ) => {
    if (!draft.plan.daily_schedule) return;
    const newDaily = [...draft.plan.daily_schedule];
    newDaily[idx] = {
      ...newDaily[idx],
      [field]: val,
    };
    onUpdatePlan({ ...draft.plan, daily_schedule: newDaily });
  };

  // Delete daily schedule card
  const handleDeleteDailyCard = (idx: number) => {
    if (!draft.plan.daily_schedule) return;
    const newDaily = [...draft.plan.daily_schedule];
    newDaily.splice(idx, 1);
    onUpdatePlan({ ...draft.plan, daily_schedule: newDaily });
  };

  // Add new daily card
  const handleAddDailyCard = () => {
    const newDaily = [...(draft.plan.daily_schedule || [])];
    newDaily.push({
      date: new Date().toISOString().split("T")[0],
      start_time: "18:00",
      end_time: "20:00",
      task: "Nhiệm vụ học tập mới",
      description: "Nhập nội dung học tập hoặc bài tập cần hoàn thành ở đây",
    });
    onUpdatePlan({ ...draft.plan, daily_schedule: newDaily });
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm">
      <div className="pb-4 border-b border-zinc-200 dark:border-zinc-850 mb-6">
        <h2 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
          Bản thảo lộ trình học đề xuất từ AI Agent (Có thể chỉnh sửa)
        </h2>
        <p className="text-[10px] text-zinc-500 font-mono mt-1 uppercase">
          Môn: {subjects.find((s) => String(s.id) === selectedSubjectId)?.name} // Điểm mong muốn: {targetScore} // Hạn chót: {deadline}
        </p>
      </div>

      <div className="space-y-6 max-h-[65vh] overflow-y-auto pr-2">
        <div className="space-y-5 text-left">
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
            📅 Lộ trình theo tuần
          </h3>
          {draft.plan.weeks.map((week, weekIdx) => (
            <div
              key={week.week}
              className="relative pl-6 border-l border-zinc-200 dark:border-zinc-800 space-y-2"
            >
              <span className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-indigo-600 border border-white dark:border-zinc-900" />
              <h4 className="text-xs font-bold text-zinc-850 dark:text-zinc-200">
                Tuần {week.week}
              </h4>
              <div className="space-y-2 pl-2">
                {week.tasks.map((task, taskIdx) => (
                  <div key={taskIdx} className="flex items-center gap-2 group">
                    <span className="text-xs text-zinc-400 font-bold">•</span>
                    <input
                      type="text"
                      value={task}
                      onChange={(e) => handleWeekTaskChange(weekIdx, taskIdx, e.target.value)}
                      className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 bg-transparent hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:bg-zinc-50 dark:focus:bg-zinc-950 px-2 py-1 border border-transparent focus:border-zinc-300 dark:focus:border-zinc-800 rounded-lg w-full focus:outline-none transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => handleDeleteWeekTask(weekIdx, taskIdx)}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-all font-extrabold text-xs cursor-pointer px-1"
                      title="Xóa nhiệm vụ"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => handleAddWeekTask(weekIdx)}
                  className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline cursor-pointer block pl-2 mt-1"
                >
                  + Thêm nhiệm vụ tuần
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-4 text-left">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">
              ⏰ Thời khóa biểu hàng ngày chi tiết
            </h3>
            <button
              type="button"
              onClick={handleAddDailyCard}
              className="text-[10px] font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 px-3 py-1 rounded-lg border border-indigo-200 dark:border-indigo-900 transition-all cursor-pointer"
            >
              + THÊM BUỔI HỌC
            </button>
          </div>
          {draft.plan.daily_schedule && draft.plan.daily_schedule.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {draft.plan.daily_schedule.map((day, idx) => (
                <div
                  key={idx}
                  className="bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/50 dark:border-zinc-850 p-4 rounded-xl space-y-3 shadow-sm relative group"
                >
                  <button
                    type="button"
                    onClick={() => handleDeleteDailyCard(idx)}
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-all font-black text-xs cursor-pointer"
                    title="Xóa buổi học"
                  >
                    ✕ Xóa
                  </button>

                  <div className="flex items-center gap-3">
                    <input
                      type="date"
                      value={day.date}
                      onChange={(e) => handleDailyScheduleFieldChange(idx, "date", e.target.value)}
                      className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-1 rounded-md font-mono border border-transparent focus:border-indigo-400 focus:outline-none"
                    />
                    <div className="flex items-center gap-1">
                      <input
                        type="time"
                        value={day.start_time}
                        onChange={(e) => handleDailyScheduleFieldChange(idx, "start_time", e.target.value)}
                        className="text-[10px] text-zinc-600 dark:text-zinc-400 bg-transparent border border-transparent focus:border-zinc-300 dark:focus:border-zinc-800 rounded px-1 focus:outline-none font-bold font-mono"
                      />
                      <span className="text-[10px] text-zinc-400">-</span>
                      <input
                        type="time"
                        value={day.end_time}
                        onChange={(e) => handleDailyScheduleFieldChange(idx, "end_time", e.target.value)}
                        className="text-[10px] text-zinc-600 dark:text-zinc-400 bg-transparent border border-transparent focus:border-zinc-300 dark:focus:border-zinc-800 rounded px-1 focus:outline-none font-bold font-mono"
                      />
                    </div>
                  </div>

                  <input
                    type="text"
                    value={day.task}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "task", e.target.value)}
                    className="w-full text-xs font-extrabold text-zinc-850 dark:text-zinc-200 bg-transparent hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:bg-zinc-50 dark:focus:bg-zinc-950 border border-transparent focus:border-zinc-300 dark:focus:border-zinc-800 rounded-lg px-2 py-1 focus:outline-none transition-all"
                  />

                  <textarea
                    rows={2}
                    value={day.description}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "description", e.target.value)}
                    className="w-full text-[10px] text-zinc-550 dark:text-zinc-400 leading-relaxed font-semibold bg-transparent hover:bg-zinc-100 dark:hover:bg-zinc-800 focus:bg-zinc-50 dark:focus:bg-zinc-950 border border-transparent focus:border-zinc-300 dark:focus:border-zinc-800 rounded-lg px-2 py-1 focus:outline-none transition-all resize-none"
                  />
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-zinc-400 font-semibold italic text-center py-6">
              Không có buổi học nào trong lịch. Vui lòng bấm thêm buổi học.
            </p>
          )}
        </div>

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
      </div>
    </div>
  );
}
