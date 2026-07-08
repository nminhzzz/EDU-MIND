"use client";

import React from "react";
import { DaySchedule, TimeSlot } from "@/features/student/types/schedule";
import {
  DAY_LABELS,
  SLOT_HOUR_OPTIONS,
  SLOT_LABELS,
} from "@/features/student/utils/schedule";

interface TimeSlotRowProps {
  day: string;
  slot: TimeSlot;
  slotData: DaySchedule[TimeSlot];
  onToggle: (day: string, slot: TimeSlot) => void;
  onHourChange: (
    day: string,
    slot: TimeSlot,
    type: "start" | "end",
    value: string,
  ) => void;
}

export function TimeSlotRow({
  day,
  slot,
  slotData,
  onToggle,
  onHourChange,
}: TimeSlotRowProps) {
  const hourOptions = SLOT_HOUR_OPTIONS[slot];

  return (
    <div className="flex flex-col space-y-2">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => onToggle(day, slot)}
          className={`px-3.5 py-1.5 rounded-xl border text-[10px] font-bold uppercase transition-all cursor-pointer ${
            slotData.enabled
              ? "bg-indigo-600 border-indigo-600 text-white shadow-sm shadow-indigo-500/10"
              : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 hover:border-zinc-350"
          }`}
        >
          {SLOT_LABELS[slot]}
        </button>
        <span className="text-[10px] text-zinc-450 dark:text-zinc-400 font-mono font-bold">
          {slotData.enabled ? `${slotData.start} - ${slotData.end}` : "Chưa chọn"}
        </span>
      </div>
      {slotData.enabled && (
        <div className="flex items-center gap-2 pl-2">
          <span className="text-[10px] text-zinc-400 font-medium">Từ:</span>
          <select
            value={slotData.start}
            onChange={(e) => onHourChange(day, slot, "start", e.target.value)}
            className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {hourOptions.start.map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
          <span className="text-[10px] text-zinc-400 font-medium">Đến:</span>
          <select
            value={slotData.end}
            onChange={(e) => onHourChange(day, slot, "end", e.target.value)}
            className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {hourOptions.end.map((h) => (
              <option key={h} value={h}>
                {h}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}

interface DayScheduleCardProps {
  day: string;
  slots: DaySchedule;
  onToggle: (day: string, slot: TimeSlot) => void;
  onHourChange: (
    day: string,
    slot: TimeSlot,
    type: "start" | "end",
    value: string,
  ) => void;
}

export function DayScheduleCard({
  day,
  slots,
  onToggle,
  onHourChange,
}: DayScheduleCardProps) {
  return (
    <div className="p-5 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-950/20 space-y-4 shadow-sm">
      <div className="pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
        <span className="text-xs font-black text-zinc-800 dark:text-zinc-200 uppercase tracking-wide">
          {DAY_LABELS[day]}
        </span>
      </div>

      <div className="space-y-3">
        <TimeSlotRow
          day={day}
          slot="morning"
          slotData={slots.morning}
          onToggle={onToggle}
          onHourChange={onHourChange}
        />
        <TimeSlotRow
          day={day}
          slot="afternoon"
          slotData={slots.afternoon}
          onToggle={onToggle}
          onHourChange={onHourChange}
        />
        <TimeSlotRow
          day={day}
          slot="evening"
          slotData={slots.evening}
          onToggle={onToggle}
          onHourChange={onHourChange}
        />
      </div>
    </div>
  );
}
