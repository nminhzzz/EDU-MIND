"use client";

import React from "react";
import { motion } from "framer-motion";
import { TimeSlot, WeekSchedule } from "@/features/student/types/schedule";
import { getFallbackDaySchedule } from "@/features/student/utils/schedule";
import { DayScheduleCard } from "./day-schedule-card";

interface GoalsScheduleStepProps {
  studyHours: number;
  preferredTime: string;
  schedule: WeekSchedule;
  loading: boolean;
  onStudyHoursChange: (value: number) => void;
  onPreferredTimeChange: (value: string) => void;
  onToggleTimeSlot: (day: string, slot: TimeSlot) => void;
  onHourChange: (
    day: string,
    slot: TimeSlot,
    type: "start" | "end",
    value: string,
  ) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function GoalsScheduleStep({
  studyHours,
  preferredTime,
  schedule,
  loading,
  onStudyHoursChange,
  onPreferredTimeChange,
  onToggleTimeSlot,
  onHourChange,
  onSubmit,
}: GoalsScheduleStepProps) {
  return (
    <motion.div
      key="setup_schedule"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="space-y-6"
    >
      <div className="bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400 p-5 rounded-2xl text-xs font-semibold leading-relaxed">
        * THÔNG BÁO: Tài khoản của bạn chưa thiết lập lịch rảnh cá nhân. Để AI Agent của EduMind phân phối giờ học chuẩn xác và không chồng lấp thời gian biểu, vui lòng hoàn tất cấu hình lịch học dưới đây trước khi lập lộ trình.
      </div>

      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm">
        <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase mb-6">
          CẤU HÌNH LỊCH HỌC CỦA BẠN
        </h2>

        <form onSubmit={onSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
              Số giờ tự học mong muốn mỗi ngày:
            </label>
            <input
              type="number"
              min={1}
              max={12}
              value={studyHours}
              onChange={(e) => onStudyHoursChange(Number(e.target.value))}
              className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
            />
            <span className="text-[10px] text-zinc-400 font-medium block">
              AI sẽ phân bổ lượng kiến thức học dựa trên số giờ tự học bạn cam kết hàng ngày.
            </span>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
              Khung giờ học ưa thích nhất:
            </label>
            <select
              value={preferredTime}
              onChange={(e) => onPreferredTimeChange(e.target.value)}
              className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
            >
              <option value="morning">Buổi sáng (08:00 - 12:00)</option>
              <option value="afternoon">Buổi chiều (13:00 - 17:00)</option>
              <option value="evening">Buổi tối (18:00 - 22:00)</option>
            </select>
          </div>

          <div className="space-y-4 border-t border-zinc-200 dark:border-zinc-800 pt-6">
            <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
              Chi tiết lịch rảnh các ngày trong tuần:
            </label>
            <span className="text-[10px] text-zinc-400 font-medium block mb-4">
              Nhấn để kích hoạt buổi bạn rảnh rỗi và cấu hình khung giờ học chi tiết cho buổi đó:
            </span>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.keys(schedule).map((day) => (
                <DayScheduleCard
                  key={day}
                  day={day}
                  slots={schedule[day] || getFallbackDaySchedule()}
                  onToggle={onToggleTimeSlot}
                  onHourChange={onHourChange}
                />
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer disabled:opacity-50"
            >
              {loading ? "ĐANG LƯU CẤU HÌNH..." : "LƯU CẤU HÌNH LỊCH HỌC & TIẾP TỤC ->"}
            </button>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
