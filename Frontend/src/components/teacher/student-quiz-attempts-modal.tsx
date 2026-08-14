"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  ClipboardList,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Calendar,
  AlertCircle,
} from "lucide-react";
import classroomApi, { ClassroomQuizAttempt } from "@/services/classroom";

interface StudentQuizAttemptsModalProps {
  open: boolean;
  onClose: () => void;
  classroomId: number;
  studentId: number;
  studentName: string;
}

export function StudentQuizAttemptsModal({
  open,
  onClose,
  classroomId,
  studentId,
  studentName,
}: StudentQuizAttemptsModalProps) {
  const [attempts, setAttempts] = useState<ClassroomQuizAttempt[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!open || !classroomId || !studentId) return;

    const fetchAttempts = async () => {
      setLoading(true);
      try {
        const res = await classroomApi.getQuizAttempts(classroomId);
        const studentAttempts = (res.data || []).filter(
          (a) => a.student_id === studentId
        );
        setAttempts(studentAttempts);
      } catch (err) {
        console.error("Lỗi lấy danh sách bài thi của học sinh:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAttempts();
  }, [open, classroomId, studentId]);

  const getScoreBadge = (score: number) => {
    if (score >= 8.0) {
      return {
        label: "Xuất sắc / Giỏi",
        color:
          "bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800",
      };
    }
    if (score >= 5.0) {
      return {
        label: "Khá / Trung bình",
        color:
          "bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800",
      };
    }
    return {
      label: "Cần cải thiện",
      color:
        "bg-rose-50 text-rose-600 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800",
    };
  };

  const formatDuration = (seconds: number) => {
    if (!seconds) return "0s";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) return `${mins}m ${secs}s`;
    return `${secs}s`;
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-50"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md shadow-2xl w-full max-w-xl max-h-[85vh] flex flex-col overflow-hidden text-left">
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-zinc-150 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-950/30 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-md bg-violet-600 text-white flex items-center justify-center font-black text-sm shadow-md shadow-violet-600/20">
                    <ClipboardList className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-black text-zinc-900 dark:text-white">
                      Danh sách bài thi — {studentName}
                    </h3>
                    <p className="text-[11px] font-medium text-zinc-400">
                      Lịch sử các bài kiểm tra đã nộp trong lớp học
                    </p>
                  </div>
                </div>

                <button
                  onClick={onClose}
                  className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-3">
                {loading ? (
                  <div className="flex flex-col items-center justify-center py-20 gap-3 text-zinc-400">
                    <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
                    <span className="text-xs font-semibold">
                      Đang tải danh sách bài thi...
                    </span>
                  </div>
                ) : attempts.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 text-center text-zinc-400 gap-2">
                    <ClipboardList className="w-10 h-10 opacity-30" />
                    <p className="text-xs font-bold text-zinc-600 dark:text-zinc-300">
                      Chưa hoàn thành bài thi nào
                    </p>
                    <p className="text-[11px] text-zinc-400">
                      Học sinh này chưa nộp bài thi nào trong lớp học này.
                    </p>
                  </div>
                ) : (
                  attempts.map((att) => {
                    const scoreNum = Number(att.score);
                    const badge = getScoreBadge(scoreNum);
                    return (
                      <div
                        key={att.attempt_id}
                        className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-md bg-zinc-50/40 dark:bg-zinc-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm hover:border-violet-200 dark:hover:border-violet-800 transition-colors"
                      >
                        <div className="space-y-1">
                          <h4 className="text-xs font-bold text-zinc-800 dark:text-zinc-100">
                            {att.quiz_title}
                          </h4>
                          <div className="flex flex-wrap items-center gap-3 text-[11px] text-zinc-400 font-medium">
                            <span className="flex items-center gap-1">
                              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                              {att.correct_count} đúng
                            </span>
                            <span className="flex items-center gap-1">
                              <XCircle className="w-3.5 h-3.5 text-rose-500" />
                              {att.wrong_count} sai
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5" />
                              {formatDuration(att.duration_seconds)}
                            </span>
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3.5 h-3.5" />
                              {new Date(att.submitted_at).toLocaleString("vi-VN")}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-3 shrink-0">
                          {att.tab_violations_count && att.tab_violations_count > 0 ? (
                            <span className="text-[10px] font-bold text-rose-600 bg-rose-50 dark:bg-rose-950/40 px-2 py-0.5 rounded border border-rose-200 dark:border-rose-800 flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" />
                              Vi phạm {att.tab_violations_count} lần
                            </span>
                          ) : null}

                          <div className="text-right">
                            <span className="text-lg font-black text-zinc-900 dark:text-white block leading-none">
                              {scoreNum.toFixed(1)}
                              <span className="text-xs font-normal text-zinc-400">/10</span>
                            </span>
                            <span
                              className={`inline-block text-[9px] font-bold px-1.5 py-0.5 rounded border mt-1 ${badge.color}`}
                            >
                              {badge.label}
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
