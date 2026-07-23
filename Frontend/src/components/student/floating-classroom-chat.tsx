"use client";

import React, { useState } from "react";
import { Users, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useStudentClassrooms } from "@/features/student/hooks/use-student-classrooms";
import { useClassroomUnread } from "@/features/student/hooks/use-classroom-unread";
import { Classroom } from "@/types/classroom";
import { useAuth } from "@/hooks/use-auth";
import { ClassroomChatList } from "./classroom-messenger/classroom-chat-list";
import { ClassroomChatPanel } from "./classroom-messenger/classroom-chat-panel";

export function FloatingClassroomChat() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedClassroom, setSelectedClassroom] = useState<Classroom | null>(null);

  const { classrooms, classroomsLoading: loading } = useStudentClassrooms();
  const { unreadCounts, totalUnread, markRead } = useClassroomUnread();

  const handleSelectClassroom = (cls: Classroom) => {
    setSelectedClassroom(cls);
    markRead(cls.id);
  };

  const isStudent = user?.role === "student";
  const positionClass = isStudent ? "bottom-[88px]" : "bottom-6";

  return (
    <div className={`fixed ${positionClass} right-6 z-50 font-sans`}>
      <AnimatePresence>
        {/* Floating Messenger Trigger Button */}
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setIsOpen(true)}
            className="w-14 h-14 rounded-full bg-violet-600 hover:bg-violet-500 text-white flex items-center justify-center shadow-lg shadow-violet-500/30 cursor-pointer active:scale-95 transition-all relative group"
            title="Thảo luận Lớp học"
          >
            <Users className="w-6 h-6" />
            {totalUnread > 0 && (
              <span className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1 bg-red-500 border-2 border-white dark:border-zinc-900 rounded-full text-[10px] font-black text-white flex items-center justify-center shadow-md shadow-red-500/40 animate-bounce">
                {totalUnread > 99 ? "99+" : totalUnread}
              </span>
            )}
          </motion.button>
        )}

        {/* Floating Chat Window Panel */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-96 h-[550px] bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden backdrop-blur-md bg-white/95 dark:bg-zinc-900/95"
          >
            {/* Main Header Bar */}
            <div className="h-14 px-4 border-b border-zinc-200 dark:border-zinc-800 bg-violet-600 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                <span className="font-extrabold text-xs tracking-wide uppercase">
                  {selectedClassroom
                    ? selectedClassroom.class_name
                    : "Thảo luận Lớp học"}
                </span>
              </div>
              <button
                onClick={() => {
                  setIsOpen(false);
                  setSelectedClassroom(null);
                }}
                className="p-1.5 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
                title="Đóng"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Container Body */}
            <div className="flex-1 overflow-y-auto bg-zinc-50 dark:bg-zinc-950/20">
              {selectedClassroom ? (
                <ClassroomChatPanel
                  classroom={selectedClassroom}
                  onBack={() => setSelectedClassroom(null)}
                  onMarkRead={markRead}
                />
              ) : (
                <ClassroomChatList
                  classrooms={classrooms}
                  unreadCounts={unreadCounts}
                  loading={loading}
                  onSelectClassroom={handleSelectClassroom}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
