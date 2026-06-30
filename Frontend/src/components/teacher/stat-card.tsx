"use client";
import React from "react";
import { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  index?: number;
}

export function StatCard({ label, value, icon: Icon, color, index = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-6 flex items-center justify-between shadow-sm rounded-xl"
    >
      <div>
        <span className="text-xs font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
          {label}
        </span>
        <span className="text-xl font-black text-zinc-900 dark:text-white mt-1 block">
          {value}
        </span>
      </div>
      <div className={`w-12 h-12 flex items-center justify-center rounded-xl ${color}`}>
        <Icon className="w-6 h-6" />
      </div>
    </motion.div>
  );
}
