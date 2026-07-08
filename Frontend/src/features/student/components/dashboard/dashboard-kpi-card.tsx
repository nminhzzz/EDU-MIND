"use client";

import React from "react";
import { motion } from "framer-motion";

interface DashboardKpiCardProps {
  label: string;
  value: React.ReactNode;
  subtitle: React.ReactNode;
  animationDelay?: number;
  children?: React.ReactNode;
}

export function DashboardKpiCard({
  label,
  value,
  subtitle,
  animationDelay = 0,
  children,
}: DashboardKpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: animationDelay }}
      className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm transition-all hover:border-zinc-300 dark:hover:border-zinc-700"
    >
      <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
        {label}
      </span>
      <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">{value}</div>
      {children}
      <span className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-2 block font-medium">
        {subtitle}
      </span>
    </motion.div>
  );
}
