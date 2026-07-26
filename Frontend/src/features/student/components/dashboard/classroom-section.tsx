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
    <div className="bg-card border border-border p-6 rounded-xl shadow-sm space-y-4">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <h2 className="font-semibold text-sm text-foreground flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-primary" />
          Lớp học tôi đã tham gia
        </h2>
        <span className="text-xs font-mono text-muted-foreground">
          {classrooms.length} lớp đã gia nhập
        </span>
      </div>

      {loading ? (
        <div className="py-8 text-center text-xs font-mono text-muted-foreground">
          Đang tải danh sách lớp học...
        </div>
      ) : classrooms.length === 0 ? (
        <div className="py-8 text-center text-sm text-muted-foreground space-y-3">
          <p>Bạn chưa tham gia lớp học nào.</p>
          <button
            onClick={onJoinClick}
            className="px-4 py-2 bg-primary/10 hover:bg-primary/15 text-primary rounded-lg text-xs font-medium transition-colors cursor-pointer"
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
