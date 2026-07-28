"use client";

import React from "react";
import { Plus, Trash2, Calendar as CalendarIcon, Clock, Sparkles, BookOpenText } from "lucide-react";
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
      description: "Nhập nội dung chi tiết bài học hoặc các dạng bài tập cần làm...",
    });
    onUpdatePlan({ ...plan, daily_schedule: newDaily });
  };

  return (
    <div className="space-y-4 w-full">
      {/* Header Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-violet-600/10 text-violet-600 dark:text-violet-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-black text-zinc-800 dark:text-zinc-200 uppercase tracking-wide">
              Lịch Học & Nhiệm Vụ Chi Tiết Từng Ngày
            </h4>
            <p className="text-[11px] text-zinc-400 font-medium">
              Bạn có thể chỉnh sửa trực tiếp tên bài học, thời gian hoặc nội dung bên dưới.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleAddDailyCard}
          className="px-4 py-2 bg-violet-600 hover:bg-violet-500 active:scale-95 text-white font-extrabold rounded-xl text-xs transition-all shadow-md shadow-violet-600/20 cursor-pointer flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" /> THÊM BUỔI HỌC MỚI
        </button>
      </div>

      {/* Daily Schedule List */}
      {plan.daily_schedule && plan.daily_schedule.length > 0 ? (
        <div className="space-y-3.5 w-full">
          {plan.daily_schedule.map((day, idx) => (
            <div
              key={idx}
              className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 p-4 sm:p-5 rounded-2xl flex flex-col md:flex-row items-stretch gap-4 shadow-xs hover:shadow-md hover:border-violet-300 dark:hover:border-violet-700/80 transition-all group"
            >
              {/* 1. Left Date & Time Card */}
              <div className="w-full md:w-64 shrink-0 flex flex-col justify-between gap-3 bg-zinc-50/80 dark:bg-zinc-950/60 p-3.5 rounded-xl border border-zinc-200/60 dark:border-zinc-800/60">
                {/* Date Picker */}
                <div className="flex items-center gap-2 bg-white dark:bg-zinc-900 px-3 py-2 rounded-lg border border-zinc-200/70 dark:border-zinc-800 shadow-2xs">
                  <CalendarIcon className="w-4 h-4 text-violet-600 dark:text-violet-400 shrink-0" />
                  <input
                    type="date"
                    value={day.date}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "date", e.target.value)}
                    className="text-xs font-black text-zinc-900 dark:text-zinc-100 bg-transparent font-mono focus:outline-none cursor-pointer w-full"
                  />
                </div>

                {/* Time Picker Range */}
                <div className="flex items-center justify-between gap-1 bg-white dark:bg-zinc-900 px-3 py-2 rounded-lg border border-zinc-200/70 dark:border-zinc-800 shadow-2xs">
                  <Clock className="w-4 h-4 text-zinc-400 shrink-0" />
                  <div className="flex items-center gap-1 min-w-0">
                    <input
                      type="time"
                      value={day.start_time}
                      onChange={(e) => handleDailyScheduleFieldChange(idx, "start_time", e.target.value)}
                      className="text-xs font-bold font-mono text-zinc-800 dark:text-zinc-200 bg-transparent focus:outline-none cursor-pointer w-16 text-center"
                    />
                    <span className="text-xs text-zinc-400 font-extrabold">-</span>
                    <input
                      type="time"
                      value={day.end_time}
                      onChange={(e) => handleDailyScheduleFieldChange(idx, "end_time", e.target.value)}
                      className="text-xs font-bold font-mono text-zinc-800 dark:text-zinc-200 bg-transparent focus:outline-none cursor-pointer w-16 text-center"
                    />
                  </div>
                </div>
              </div>

              {/* 2. Middle Content Area: Task Title & Description */}
              <div className="flex-1 space-y-2.5 min-w-0">
                {/* Main Task Title Input */}
                <div className="relative">
                  <input
                    type="text"
                    spellCheck={false}
                    value={day.task}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "task", e.target.value)}
                    placeholder="Tên bài học hoặc nhiệm vụ chính..."
                    className="w-full text-sm font-black text-zinc-900 dark:text-white bg-zinc-50/50 dark:bg-zinc-950/40 border border-zinc-200/80 dark:border-zinc-800 focus:border-violet-500 focus:bg-white dark:focus:bg-zinc-900 rounded-xl px-3.5 py-2 focus:outline-none transition-all placeholder:text-zinc-400"
                  />
                </div>

                {/* Detailed Description Textarea */}
                <div className="relative">
                  <textarea
                    rows={2}
                    spellCheck={false}
                    value={day.description}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "description", e.target.value)}
                    placeholder="Chi tiết nội dung bài học, dạng bài tập và lý thuyết cần đạt..."
                    className="w-full text-xs font-medium text-zinc-700 dark:text-zinc-300 leading-relaxed bg-zinc-50/50 dark:bg-zinc-950/40 border border-zinc-200/80 dark:border-zinc-800 focus:border-violet-500 focus:bg-white dark:focus:bg-zinc-900 rounded-xl px-3.5 py-2.5 focus:outline-none transition-all resize-y min-h-[56px] placeholder:text-zinc-400"
                  />
                </div>
              </div>

              {/* 3. Right Action Column: Delete Button */}
              <div className="shrink-0 flex md:flex-col items-center justify-center border-t md:border-t-0 md:border-l border-zinc-100 dark:border-zinc-800/80 pt-2.5 md:pt-0 md:pl-3">
                <button
                  type="button"
                  onClick={() => handleDeleteDailyCard(idx)}
                  className="p-2.5 rounded-xl text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold"
                  title="Xóa buổi học này"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="md:hidden text-red-600">Xóa buổi học</span>
                </button>
              </div>
            </div>
          ))}

          {/* Add New Session Dashed Button */}
          <button
            type="button"
            onClick={handleAddDailyCard}
            className="w-full py-3.5 border-2 border-dashed border-zinc-200 dark:border-zinc-800 hover:border-violet-500 dark:hover:border-violet-500 rounded-2xl text-xs font-extrabold text-zinc-500 hover:text-violet-600 dark:hover:text-violet-400 transition-all cursor-pointer flex items-center justify-center gap-2 mt-4 bg-zinc-50/40 dark:bg-zinc-950/20"
          >
            <Plus className="w-4 h-4" /> THÊM BUỔI HỌC MỚI VÀO LỊCH HỌC
          </button>
        </div>
      ) : (
        <div className="p-8 text-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-2xl space-y-3 bg-zinc-50/50 dark:bg-zinc-950/30">
          <BookOpenText className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-1" />
          <p className="text-xs text-zinc-400 font-semibold italic">
            Chưa có buổi học nào trong thời khóa biểu chi tiết.
          </p>
          <button
            type="button"
            onClick={handleAddDailyCard}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-xl text-xs font-extrabold inline-flex items-center gap-1.5 shadow-md shadow-violet-600/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Thêm buổi học đầu tiên
          </button>
        </div>
      )}
    </div>
  );
}
