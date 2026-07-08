"use client";

import React from "react";
import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";
import { ClassroomStudentProgress } from "@/services/classroom";

interface StudentProgressTableProps {
  students: ClassroomStudentProgress[];
}

export function StudentProgressTable({ students }: StudentProgressTableProps) {
  if (students.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-400 dark:text-zinc-500">
        <BarChart3 className="w-10 h-10 mx-auto mb-3 opacity-40" />
        <p className="text-sm font-medium">Chưa có dữ liệu tiến độ học tập.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800">
            <th className="text-left py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              Học sinh
            </th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              Mục tiêu
            </th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              Bài làm
            </th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              Điểm TB
            </th>
          </tr>
        </thead>
        <tbody>
          {students.map((student, idx) => (
            <motion.tr
              key={student.student_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.03 }}
              className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors"
            >
              <td className="py-3 px-4">
                <div>
                  <p className="font-semibold text-zinc-800 dark:text-zinc-200">
                    {student.full_name || `Học sinh #${student.student_id}`}
                  </p>
                  <p className="text-xs text-zinc-400">{student.email}</p>
                </div>
              </td>
              <td className="py-3 px-4 text-center text-zinc-600 dark:text-zinc-400">
                <span className="text-emerald-500">{student.completed_goals}</span>
                <span className="text-zinc-300 dark:text-zinc-600 mx-1">/</span>
                <span>{student.total_goals}</span>
              </td>
              <td className="py-3 px-4 text-center text-zinc-600 dark:text-zinc-400">
                {student.total_attempts}
              </td>
              <td className="py-3 px-4 text-center">
                {student.average_score != null ? (
                  <span
                    className={`inline-block px-2.5 py-1 rounded-lg text-xs font-bold ${
                      student.average_score >= 8
                        ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400"
                        : student.average_score >= 5
                          ? "text-amber-600 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400"
                          : "text-red-600 bg-red-50 dark:bg-red-950/30 dark:text-red-400"
                    }`}
                  >
                    {student.average_score.toFixed(1)}
                  </span>
                ) : (
                  <span className="text-zinc-400">—</span>
                )}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
