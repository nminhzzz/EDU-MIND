"use client";

import React from "react";
import { MessageSquare, Loader2, Users } from "lucide-react";
import { Classroom } from "@/types/classroom";

import { useAuth } from "@/hooks/use-auth";

interface ClassroomChatListProps {
  classrooms: Classroom[];
  unreadCounts: Record<number, number>;
  loading: boolean;
  onSelectClassroom: (classroom: Classroom) => void;
}

export function ClassroomChatList({
  classrooms,
  unreadCounts,
  loading,
  onSelectClassroom,
}: ClassroomChatListProps) {
  const { user } = useAuth();
  const isTeacher = user?.role === "teacher";

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-zinc-400 gap-2">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <span className="text-xs">Đang tải danh sách lớp...</span>
      </div>
    );
  }

  if (classrooms.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-400 p-4">
        <Users className="w-10 h-10 text-zinc-300 dark:text-zinc-700 mb-2" />
        <p className="text-xs font-bold text-zinc-600 dark:text-zinc-300">
          {isTeacher ? "Chưa có lớp học nào" : "Chưa tham gia lớp học nào"}
        </p>
        <p className="text-[11px] text-zinc-400 mt-1">
          {isTeacher
            ? "Hãy tạo lớp học mới để giảng dạy và trao đổi cùng học sinh!"
            : "Hãy nhập mã lớp học để tham gia và trao đổi cùng các bạn nhé!"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2 p-3">
      {classrooms.map((cls) => {
        const unread = unreadCounts[cls.id] || 0;
        return (
          <button
            key={cls.id}
            onClick={() => onSelectClassroom(cls)}
            className="w-full flex items-center justify-between p-3.5 rounded-xl border border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/20 hover:border-indigo-200 dark:hover:border-indigo-800 transition-all text-left group cursor-pointer shadow-sm"
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-black text-xs shrink-0 group-hover:scale-105 transition-transform">
                <MessageSquare className="w-5 h-5" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-zinc-800 dark:text-zinc-100 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {cls.class_name}
                </p>
                <p className="text-[10px] font-mono text-zinc-400 dark:text-zinc-500 mt-0.5">
                  Mã lớp: {cls.class_code}
                </p>
              </div>
            </div>

            {unread > 0 && (
              <div className="ml-2 px-2 py-0.5 bg-red-500 text-white text-[11px] font-black rounded-full shadow-md shadow-red-500/30 shrink-0 animate-pulse">
                {unread > 99 ? "99+" : unread}
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
