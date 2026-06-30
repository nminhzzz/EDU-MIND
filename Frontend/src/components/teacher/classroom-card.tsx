"use client";
import React from "react";
import Link from "next/link";
import { Users, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";

interface ClassroomCardProps {
  id: number;
  className_: string;
  classCode: string;
  studentCount: number;
  subjectId: number;
  index?: number;
}

export function ClassroomCard({ id, className_, classCode, studentCount, index = 0 }: ClassroomCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      className="group p-5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-900 hover:border-violet-300 dark:hover:border-violet-700 hover:shadow-md transition-all duration-200"
    >
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-zinc-800 dark:text-zinc-200 truncate">{className_}</h3>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs font-mono text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/40 px-2 py-0.5 rounded-md">
              {classCode}
            </span>
            <span className="text-xs text-zinc-400 dark:text-zinc-500 flex items-center gap-1">
              <Users className="w-3.5 h-3.5" />
              {studentCount} học sinh
            </span>
          </div>
        </div>
        <Link
          href={`/teacher/classrooms/${id}`}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 hover:bg-violet-100 dark:hover:bg-violet-900/50"
        >
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>
    </motion.div>
  );
}
