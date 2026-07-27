"use client";

import React from "react";
import { GraduationCap, Sparkles } from "lucide-react";
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
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 md:p-8 rounded-3xl shadow-sm space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-extrabold text-base text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
              Lớp học tôi đã tham gia
            </h2>
            <p className="text-[11px] text-zinc-400 dark:text-zinc-500 font-medium">
              Kết nối trực tiếp với giáo viên và các bạn học sinh trong lớp
            </p>
          </div>
        </div>

        <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900/40 px-3 py-1 rounded-xl">
          {classrooms.length} lớp đã gia nhập
        </span>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs font-mono text-zinc-400">
          Đang tải danh sách lớp học...
        </div>
      ) : classrooms.length === 0 ? (
        <div className="py-12 text-center text-sm text-zinc-500 dark:text-zinc-400 space-y-4">
          <p className="font-medium">Bạn chưa tham gia lớp học nào.</p>
          <button
            onClick={onJoinClick}
            className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-500/20 active:scale-95 cursor-pointer inline-flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Gia nhập lớp học ngay
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {classrooms.map((cls) => (
            <ClassroomCard key={cls.id} classroom={cls} onClick={onSelectClassroom} />
          ))}
        </div>
      )}
    </div>
  );
}

