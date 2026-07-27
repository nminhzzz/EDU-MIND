"use client";

import React from "react";
import type { Classroom } from "@/features/student/types";
import { BookOpen, Users, ChevronRight, Sparkles } from "lucide-react";

interface ClassroomCardProps {
  classroom: Classroom;
  onClick: (classroom: Classroom) => void;
}

const ACCENT_GRADIENTS = [
  "from-indigo-600 to-violet-600",
  "from-emerald-500 to-teal-600",
  "from-amber-500 to-orange-600",
  "from-purple-600 to-pink-600",
  "from-sky-500 to-blue-600",
];

export function ClassroomCard({ classroom, onClick }: ClassroomCardProps) {
  const gradientIndex = (classroom.id || 0) % ACCENT_GRADIENTS.length;
  const gradientClass = ACCENT_GRADIENTS[gradientIndex];

  return (
    <div
      onClick={() => onClick(classroom)}
      className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-5 shadow-sm hover:shadow-xl hover:border-indigo-400 dark:hover:border-indigo-500 hover:-translate-y-1 transition-all duration-300 cursor-pointer text-left"
    >
      {/* Top Accent Gradient Bar */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r ${gradientClass}`} />

      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="p-2.5 rounded-xl bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-200">
            <BookOpen className="w-4 h-4" />
          </div>

          <span className="text-[11px] font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900/40 px-2.5 py-1 rounded-lg">
            {classroom.class_code}
          </span>
        </div>

        <div>
          <h3 className="text-base font-black text-zinc-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-1">
            {classroom.class_name}
          </h3>
          <p className="text-[11px] text-zinc-400 dark:text-zinc-500 font-medium mt-0.5 line-clamp-1">
            {classroom.description || "Lớp học tương tác với Gia sư AI & Giáo viên"}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 mt-3 border-t border-zinc-100 dark:border-zinc-850">
        <div className="flex items-center gap-1.5 text-[11px] font-bold text-zinc-500 dark:text-zinc-400">
          <Users className="w-3.5 h-3.5 text-zinc-400" />
          <span>Vào phòng trao đổi</span>
        </div>

        <div className="w-6 h-6 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-all duration-200">
          <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
}

