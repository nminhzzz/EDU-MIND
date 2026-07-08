"use client";

import React from "react";
import { GraduationCap } from "lucide-react";
import type { Classroom } from "@/features/student/types";
import { ClassroomCard } from "./classroom-card";

interface ClassroomSectionProps {
  classrooms: Classroom[];
  loading: boolean;
  onJoinClick: () => void;
  onSelectClassroom: (classroom: Classroom) => void;
}

export function ClassroomSection({
  classrooms,
  loading,
  onJoinClick,
  onSelectClassroom,
}: ClassroomSectionProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800">
        <h2 className="font-extrabold text-sm text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-indigo-500" />
          Lớp học tôi đã tham gia
        </h2>
        <span className="text-xs font-mono text-zinc-400 dark:text-zinc-500">
          {classrooms.length} lớp đã gia nhập
        </span>
      </div>

      {loading ? (
        <div className="py-8 text-center text-xs font-mono text-zinc-400">
          Đang tải danh sách lớp học...
        </div>
      ) : classrooms.length === 0 ? (
        <div className="py-8 text-center text-sm text-zinc-500 dark:text-zinc-400 space-y-3">
          <p>Bạn chưa tham gia lớp học nào.</p>
          <button
            onClick={onJoinClick}
            className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 dark:text-indigo-400 rounded-xl text-xs font-bold transition-all cursor-pointer"
          >
            Gia nhập lớp học ngay
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {classrooms.map((cls) => (
            <ClassroomCard key={cls.id} classroom={cls} onClick={onSelectClassroom} />
          ))}
        </div>
      )}
    </div>
  );
}
