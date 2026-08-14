"use client";

import React from "react";
import type { Classroom } from "@/features/student/types";
import { BookOpen, Users, ChevronRight, Sparkles } from "lucide-react";

interface ClassroomCardProps {
  classroom: Classroom;
  onClick: (classroom: Classroom) => void;
}

const ACCENT_BARS = [
  "bg-gradient-to-r from-sky-400 to-blue-500",
  "bg-gradient-to-r from-cyan-400 to-sky-500",
  "bg-gradient-to-r from-blue-400 to-sky-600",
  "bg-gradient-to-r from-sky-500 to-teal-500",
];

export function ClassroomCard({ classroom, onClick }: ClassroomCardProps) {
  const barIndex = (classroom.id || 0) % ACCENT_BARS.length;
  const barClass = ACCENT_BARS[barIndex];

  return (
    <div
      onClick={() => onClick(classroom)}
      className="group relative flex flex-col justify-between overflow-hidden rounded-md border border-sky-200/80 dark:border-sky-900/50 bg-white dark:bg-sky-950/40 p-5 shadow-xs hover:shadow-md hover:border-sky-300 dark:hover:border-sky-700 hover:-translate-y-0.5 transition-all duration-300 cursor-pointer text-left"
    >
      {/* Top Accent Bar */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${barClass}`} />

      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="p-2.5 rounded-md bg-sky-50 dark:bg-sky-900/50 text-sky-600 dark:text-sky-300 border border-sky-100 dark:border-sky-800 group-hover:bg-sky-600 group-hover:text-white group-hover:border-sky-600 transition-colors duration-200">
            <BookOpen className="w-4 h-4" />
          </div>

          <span className="text-[11px] font-mono font-bold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-900/60 border border-sky-200/80 dark:border-sky-800 px-2.5 py-1 rounded-md shadow-xs">
            {classroom.class_code}
          </span>
        </div>

        <div>
          <h3 className="text-base font-black text-sky-950 dark:text-white group-hover:text-sky-600 dark:group-hover:text-sky-300 transition-colors line-clamp-1">
            {classroom.class_name}
          </h3>
          <p className="text-[11px] text-sky-900/70 dark:text-sky-300/70 font-medium mt-0.5 line-clamp-1">
            {classroom.description || "Lớp học tương tác với Gia sư AI & Giáo viên"}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 mt-3 border-t border-sky-100 dark:border-sky-900/50">
        <div className="flex items-center gap-1.5 text-[11px] font-bold text-sky-700/80 dark:text-sky-300/80">
          <Users className="w-3.5 h-3.5 text-sky-500/80" />
          <span>Vào phòng trao đổi</span>
        </div>

        <div className="w-6 h-6 rounded-md bg-sky-50 dark:bg-sky-900/50 border border-sky-200/60 dark:border-sky-800 flex items-center justify-center group-hover:bg-sky-600 group-hover:text-white group-hover:border-sky-600 transition-all duration-200">
          <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
}

