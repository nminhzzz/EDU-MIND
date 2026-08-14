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
  iconBg = "bg-white dark:bg-sky-900/50 border border-sky-200 dark:border-sky-800",
  iconColor = "text-sky-600 dark:text-sky-300",
  children,
}: DashboardKpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: animationDelay }}
      className="relative overflow-hidden bg-sky-50/40 dark:bg-sky-950/30 border border-sky-200/70 dark:border-sky-900/40 p-6 rounded-2xl shadow-xs hover:shadow-md hover:border-sky-300 dark:hover:border-sky-800 transition-all group"
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-[11px] font-extrabold text-sky-700/80 dark:text-sky-300/80 uppercase tracking-wider block">
            {label}
          </span>
          <div className="text-3xl font-black text-sky-950 dark:text-white tracking-tight">
            {value}
          </div>
        </div>

        {Icon && (
          <div className={`p-3 rounded-2xl ${iconBg} ${iconColor} shadow-xs group-hover:scale-110 transition-transform duration-200`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      {children}

      <div className="text-[11px] text-sky-800/80 dark:text-sky-300/80 mt-3 font-semibold flex items-center gap-1.5">
        {subtitle}
      </div>
    </motion.div>
  );
}

