"use client";

import React from "react";
import { Plus, Trash2, Calendar as CalendarIcon, Clock, BookOpenText } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";
import { Button } from "@/components/ui";

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
    <div className="w-full space-y-5">
      {/* Header Toolbar */}
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <h4 className="text-base font-bold text-zinc-900 dark:text-white">
              Lịch học chi tiết
            </h4>
            <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
              Chỉnh sửa trực tiếp từng buổi học trước khi xác nhận.
            </p>
          </div>
        <Button size="sm" onClick={handleAddDailyCard}><Plus className="size-4" /> Thêm buổi học</Button>
      </div>

      {/* Daily Schedule List */}
      {plan.daily_schedule && plan.daily_schedule.length > 0 ? (
        <div className="w-full space-y-3">
          {plan.daily_schedule.map((day, idx) => (
            <div
              key={idx}
              className="grid items-stretch gap-4 rounded-xl border border-zinc-200 bg-white p-4 transition-colors hover:border-indigo-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-indigo-800 md:grid-cols-[200px_minmax(0,1fr)_44px]"
            >
              {/* 1. Left Date & Time Card */}
              <div className="flex w-full shrink-0 flex-col justify-center gap-2 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-950/40">
                {/* Date Picker */}
                <div className="flex items-center gap-2">
                  <CalendarIcon className="w-4 h-4 text-violet-600 dark:text-violet-400 shrink-0" />
                  <input
                    type="date"
                    value={day.date}
                    onChange={(e) => handleDailyScheduleFieldChange(idx, "date", e.target.value)}
                    className="text-xs font-black text-zinc-900 dark:text-zinc-100 bg-transparent font-mono focus:outline-none cursor-pointer w-full"
                  />
                </div>

                {/* Time Picker Range */}
                <div className="flex items-center justify-between gap-1">
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
                    className="w-full rounded-lg border border-zinc-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 dark:border-zinc-800 dark:bg-zinc-900 dark:text-white"
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
                    className="min-h-[64px] w-full resize-y rounded-lg border border-zinc-200 bg-white px-3.5 py-2.5 text-sm leading-relaxed text-zinc-700 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300"
                  />
                </div>
              </div>

              {/* 3. Right Action Column: Delete Button */}
              <div className="flex shrink-0 items-center justify-end border-t border-zinc-100 pt-2 md:justify-center md:border-l md:border-t-0 md:pl-3 md:pt-0 dark:border-zinc-800">
                <button
                  type="button"
                  onClick={() => handleDeleteDailyCard(idx)}
                  className="p-2.5 rounded-md text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all cursor-pointer flex items-center gap-1.5 text-xs font-bold"
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
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-zinc-300 bg-zinc-50/50 py-3.5 text-sm font-semibold text-zinc-600 transition-colors hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 dark:border-zinc-700 dark:bg-zinc-950/20 dark:text-zinc-400 dark:hover:border-indigo-700 dark:hover:bg-indigo-950/20"
          >
            <Plus className="w-4 h-4" /> Thêm buổi học mới
          </button>
        </div>
      ) : (
        <div className="p-8 text-center border-2 border-dashed border-zinc-200 dark:border-zinc-800 rounded-md space-y-3 bg-zinc-50/50 dark:bg-zinc-950/30">
          <BookOpenText className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-1" />
          <p className="text-xs text-zinc-400 font-semibold italic">
            Chưa có buổi học nào trong thời khóa biểu chi tiết.
          </p>
          <button
            type="button"
            onClick={handleAddDailyCard}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-md text-xs font-extrabold inline-flex items-center gap-1.5 shadow-md shadow-violet-600/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Thêm buổi học đầu tiên
          </button>
        </div>
      )}
    </div>
  );
}
