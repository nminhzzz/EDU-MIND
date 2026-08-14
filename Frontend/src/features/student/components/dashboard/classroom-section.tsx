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
    <div className="bg-sky-50/30 dark:bg-sky-950/20 border border-sky-200/70 dark:border-sky-900/40 p-6 md:p-8 rounded-3xl shadow-xs space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-sky-200/60 dark:border-sky-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-white dark:bg-sky-900/50 border border-sky-200 dark:border-sky-800 text-sky-600 dark:text-sky-300 shadow-xs">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-extrabold text-base text-sky-950 dark:text-white flex items-center gap-2">
              Lớp học tôi đã tham gia
            </h2>
            <p className="text-[11px] text-sky-900/70 dark:text-sky-300/70 font-medium">
              Kết nối trực tiếp với giáo viên và các bạn học sinh trong lớp
            </p>
          </div>
        </div>

        <span className="text-xs font-mono font-bold text-sky-700 dark:text-sky-300 bg-white dark:bg-sky-900/60 border border-sky-200 dark:border-sky-800 px-3 py-1 rounded-xl shadow-xs">
          {classrooms.length} lớp đã gia nhập
        </span>
      </div>

      {loading ? (
        <div className="py-12 text-center text-xs font-mono text-sky-600/70 dark:text-sky-400/70">
          Đang tải danh sách lớp học...
        </div>
      ) : classrooms.length === 0 ? (
        <div className="py-12 text-center text-sm text-sky-900/70 dark:text-sky-300/70 space-y-4">
          <p className="font-medium">Bạn chưa tham gia lớp học nào.</p>
          <button
            onClick={onJoinClick}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-400 text-white dark:text-slate-950 border border-sky-600 rounded-xl text-xs font-bold transition-all shadow-md shadow-sky-500/15 active:scale-95 cursor-pointer inline-flex items-center gap-2"
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-100 dark:text-slate-900" />
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

