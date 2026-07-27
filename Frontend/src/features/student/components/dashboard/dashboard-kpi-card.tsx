"use client";

import React from "react";
import { motion } from "framer-motion";

interface DashboardKpiCardProps {
  label: string;
  value: React.ReactNode;
  subtitle: React.ReactNode;
  animationDelay?: number;
  icon?: React.ElementType;
  iconBg?: string;
  iconColor?: string;
  children?: React.ReactNode;
}

export function DashboardKpiCard({
  label,
  value,
  subtitle,
  animationDelay = 0,
  icon: Icon,
  iconBg = "bg-indigo-50 dark:bg-indigo-950/50",
  iconColor = "text-indigo-600 dark:text-indigo-400",
  children,
}: DashboardKpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: animationDelay }}
      className="relative overflow-hidden bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm hover:shadow-md hover:border-zinc-300 dark:hover:border-zinc-700 transition-all group"
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            {label}
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
            {value}
          </div>
        </div>

        {Icon && (
          <div className={`p-3 rounded-2xl ${iconBg} ${iconColor} shadow-inner group-hover:scale-110 transition-transform duration-200`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      {children}

      <div className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-3 font-semibold flex items-center gap-1.5">
        {subtitle}
      </div>
    </motion.div>
  );
}

