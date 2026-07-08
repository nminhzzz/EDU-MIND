"use client";

import React from "react";
import type { Classroom } from "@/features/student/types";

interface ClassroomCardProps {
  classroom: Classroom;
  onClick: (classroom: Classroom) => void;
}

export function ClassroomCard({ classroom, onClick }: ClassroomCardProps) {
  return (
    <div
      onClick={() => onClick(classroom)}
      className="group p-5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-900 hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-sm transition-all duration-200 cursor-pointer text-left"
    >
      <h3 className="text-sm font-bold text-zinc-800 dark:text-zinc-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
        {classroom.class_name}
      </h3>
      <div className="flex items-center gap-3 mt-2">
        <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md">
          {classroom.class_code}
        </span>
      </div>
    </div>
  );
}
