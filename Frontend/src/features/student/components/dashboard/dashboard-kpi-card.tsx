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
      className="bg-card border border-border p-6 rounded-xl shadow-sm transition-colors hover:border-ring/40"
    >
      <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide block">
        {label}
      </span>
      <div className="text-3xl font-bold text-foreground mt-1 tracking-tight">{value}</div>
      {children}
      <span className="text-xs text-muted-foreground mt-2 block">
        {subtitle}
      </span>
    </motion.div>
  );
}
