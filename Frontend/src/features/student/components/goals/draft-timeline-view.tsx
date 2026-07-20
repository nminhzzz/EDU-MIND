"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronRight, Plus, Trash2 } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";

interface DraftTimelineViewProps {
  plan: RoadmapPlan;
  onUpdatePlan: (updatedPlan: RoadmapPlan) => void;
}

export function DraftTimelineView({ plan, onUpdatePlan }: DraftTimelineViewProps) {
  const [expandedWeeks, setExpandedWeeks] = useState<Record<number, boolean>>({ 1: true });

  const toggleWeek = (weekNum: number) => {
    setExpandedWeeks((prev) => ({ ...prev, [weekNum]: !prev[weekNum] }));
  };

  const handleWeekTaskChange = (weekIdx: number, taskIdx: number, val: string) => {
    const newWeeks = [...plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks],
    };
    newWeeks[weekIdx].tasks[taskIdx] = val;
    onUpdatePlan({ ...plan, weeks: newWeeks });
  };

  const handleAddWeekTask = (weekIdx: number) => {
    const newWeeks = [...plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks, "Nhiệm vụ tuần mới"],
    };
    onUpdatePlan({ ...plan, weeks: newWeeks });
  };

  const handleDeleteWeekTask = (weekIdx: number, taskIdx: number) => {
    const newWeeks = [...plan.weeks];
    newWeeks[weekIdx] = {
      ...newWeeks[weekIdx],
      tasks: [...newWeeks[weekIdx].tasks],
    };
    newWeeks[weekIdx].tasks.splice(taskIdx, 1);
    onUpdatePlan({ ...plan, weeks: newWeeks });
  };

  return (
    <div className="space-y-4 w-full">
      {plan.weeks.map((week, weekIdx) => {
        const isExpanded = expandedWeeks[week.week] !== false; // expanded by default

        return (
          <div
            key={week.week}
            className="border border-zinc-200/80 dark:border-zinc-800 rounded-2xl bg-white dark:bg-zinc-950 overflow-hidden transition-all shadow-sm w-full"
          >
            {/* Week Header */}
            <div
              onClick={() => toggleWeek(week.week)}
              className="p-4 flex items-center justify-between cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-xl bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 font-mono font-black text-xs flex items-center justify-center border border-indigo-500/20 shrink-0">
                  W{week.week}
                </div>
                <div>
                  <h4 className="text-xs font-extrabold text-zinc-900 dark:text-white uppercase">
                    Tuần {week.week} - Lộ trình mục tiêu
                  </h4>
                  <span className="text-[10px] text-zinc-400 font-semibold block">
                    {week.tasks.length} nhiệm vụ đã được thiết lập
                  </span>
                </div>
              </div>

              <div className="text-zinc-400">
                {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </div>
            </div>

            {/* Week Tasks Content */}
            {isExpanded && (
              <div className="px-4 pb-4 pt-1 border-t border-zinc-100 dark:border-zinc-900 space-y-2">
                {week.tasks.map((task, taskIdx) => (
                  <div key={taskIdx} className="flex items-center gap-2 group">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
                    <input
                      type="text"
                      value={task}
                      onChange={(e) => handleWeekTaskChange(weekIdx, taskIdx, e.target.value)}
                      className="text-xs font-semibold text-zinc-700 dark:text-zinc-300 bg-transparent hover:bg-zinc-100 dark:hover:bg-zinc-900 focus:bg-zinc-50 dark:focus:bg-zinc-950 px-2.5 py-1.5 border border-transparent focus:border-indigo-500/40 rounded-xl w-full focus:outline-none transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => handleDeleteWeekTask(weekIdx, taskIdx)}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-all cursor-pointer p-1"
                      title="Xóa nhiệm vụ"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}

                <button
                  type="button"
                  onClick={() => handleAddWeekTask(weekIdx)}
                  className="mt-2 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 cursor-pointer pl-1"
                >
                  <Plus className="w-3 h-3" /> Thêm nhiệm vụ tuần
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
