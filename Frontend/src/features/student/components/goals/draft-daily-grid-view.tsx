"use client";

import React from "react";
import { Plus, Trash2, Calendar as CalendarIcon, Clock } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";

interface DraftDailyGridViewProps {
  plan: RoadmapPlan;
  onUpdatePlan: (updatedPlan: RoadmapPlan) => void;
}

export function DraftDailyGridView({ plan, onUpdatePlan }: DraftDailyGridViewProps) {
  const handleDailyScheduleFieldChange = (
    idx: number,
    field: "date" | "start_time" | "end_time" | "task" | "description",
    val: string
  ) => {
    if (!plan.daily_schedule) return;
    const newDaily = [...plan.daily_schedule];
    newDaily[idx] = {
      ...newDaily[idx],
      [field]: val,
    };
    onUpdatePlan({ ...plan, daily_schedule: newDaily });
  };

  const handleDeleteDailyCard = (idx: number) => {
    if (!plan.daily_schedule) return;
    const newDaily = [...plan.daily_schedule];
    newDaily.splice(idx, 1);
    onUpdatePlan({ ...plan, daily_schedule: newDaily });
  };

  const handleAddDailyCard = () => {
    const newDaily = [...(plan.daily_schedule || [])];
    newDaily.push({
      date: new Date().toISOString().split("T")[0],
      start_time: "18:00",
      end_time: "20:00",
      task: "Nhiệm vụ học tập mới",
      description: "Nhập nội dung học tập hoặc bài tập cần hoàn thành ở đây",
    });
    onUpdatePlan({ ...plan, daily_schedule: newDaily });
  };

  return (
    <div className="space-y-4 w-full">
      <div className="flex justify-between items-center pb-2">
        <h4 className="text-xs font-black text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
          ⏰ Thời khóa biểu chi tiết từng ngày (1 Ngày = 1 Hàng Ngang)
        </h4>
        <button
          type="button"
          onClick={handleAddDailyCard}
          className="text-xs font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 px-4 py-2 rounded-xl border border-indigo-200 dark:border-indigo-900 transition-all cursor-pointer flex items-center gap-1.5 shadow-sm"
        >
          <Plus className="w-4 h-4" /> THÊM BUỔI HỌC MỚI
        </button>
      </div>

      {plan.daily_schedule && plan.daily_schedule.length > 0 ? (
        <div className="space-y-3.5 w-full">
          {plan.daily_schedule.map((day, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-zinc-950 border border-zinc-200/80 dark:border-zinc-800 p-5 rounded-2xl flex flex-col md:flex-row items-stretch gap-4 shadow-sm hover:border-zinc-300 dark:hover:border-zinc-700 transition-all group"
            >
              {/* Left Column: Date & Time Badges */}
              <div className="w-full md:w-64 shrink-0 flex flex-col justify-between gap-2.5 bg-zinc-50 dark:bg-zinc-900/50 p-3.5 rounded-xl border border-zinc-200/50 dark:border-zinc-800">
                <div className="flex items-center gap-2">
                  <CalendarIcon className="w-4 h-4 text-indigo-600 dark:text-indigo-400 shrink-0" />
                  <input
                    type="date"
                    value={day.date}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "date", e.target.value)}
                    className="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-transparent font-mono focus:outline-none cursor-pointer w-full"
                  />
                </div>

                <div className="flex items-center gap-1.5 pt-2 border-t border-zinc-200/60 dark:border-zinc-800">
                  <Clock className="w-4 h-4 text-zinc-400 shrink-0" />
                  <input
                    type="time"
                    value={day.start_time}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "start_time", e.target.value)}
                    className="text-xs text-zinc-700 dark:text-zinc-300 bg-transparent focus:outline-none font-bold font-mono cursor-pointer w-full"
                  />
                  <span className="text-xs text-zinc-400 font-bold">-</span>
                  <input
                    type="time"
                    value={day.end_time}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "end_time", e.target.value)}
                    className="text-xs text-zinc-700 dark:text-zinc-300 bg-transparent focus:outline-none font-bold font-mono cursor-pointer w-full"
                  />
                </div>
              </div>

              {/* Middle Column: Main Task & Description */}
              <div className="flex-1 space-y-2">
                <div>
                  <label className="block text-[10px] font-bold text-zinc-400 uppercase mb-1">
                    Tên bài học / Nhiệm vụ chính:
                  </label>
                  <input
                    type="text"
                    value={day.task}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "task", e.target.value)}
                    placeholder="Nhập tên bài học..."
                    className="w-full text-sm font-black text-zinc-900 dark:text-white bg-zinc-50/60 dark:bg-zinc-900/60 border border-zinc-200/80 dark:border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 focus:outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-zinc-400 uppercase mb-1">
                    Nội dung chi tiết & Bài tập:
                  </label>
                  <textarea
                    rows={2}
                    value={day.description}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "description", e.target.value)}
                    placeholder="Mô tả nội dung chi tiết bài học..."
                    className="w-full text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed font-medium bg-zinc-50/60 dark:bg-zinc-900/60 border border-zinc-200/80 dark:border-zinc-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 focus:outline-none transition-all resize-y min-h-[60px]"
                  />
                </div>
              </div>

              {/* Right Column: Actions */}
              <div className="shrink-0 flex md:flex-col items-center justify-between md:justify-center border-t md:border-t-0 md:border-l border-zinc-100 dark:border-zinc-800 pt-3 md:pt-0 md:pl-4">
                <button
                  type="button"
                  onClick={() => handleDeleteDailyCard(idx)}
                  className="px-3 py-2 rounded-xl text-red-500 hover:text-white hover:bg-red-500 transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold"
                  title="Xóa buổi học này"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="md:hidden">Xóa</span>
                </button>
              </div>
            </div>
          ))}

          <button
            type="button"
            onClick={handleAddDailyCard}
            className="w-full py-4 border-2 border-dashed border-zinc-200 dark:border-zinc-800 hover:border-indigo-500 dark:hover:border-indigo-500 rounded-2xl text-xs font-black text-zinc-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all cursor-pointer flex items-center justify-center gap-2 mt-4"
          >
            <Plus className="w-4 h-4" /> THÊM BUỔI HỌC MỚI VÀO LỊCH
          </button>
        </div>
      ) : (
        <div className="p-8 text-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl space-y-3">
          <p className="text-xs text-zinc-400 font-semibold italic">
            Chưa có buổi học nào trong thời khóa biểu chi tiết.
          </p>
          <button
            type="button"
            onClick={handleAddDailyCard}
            className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold inline-flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Thêm buổi học đầu tiên
          </button>
        </div>
      )}
    </div>
  );
}
