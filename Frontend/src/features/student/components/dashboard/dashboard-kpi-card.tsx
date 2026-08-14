"use client";

import React from "react";
import { Card } from "@/components/ui";

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
  icon: Icon,
  iconBg = "bg-white dark:bg-sky-900/50 border border-sky-200 dark:border-sky-800",
  iconColor = "text-sky-600 dark:text-sky-300",
  children,
}: DashboardKpiCardProps) {
  return (
    <Card className="group relative overflow-hidden p-5 transition-colors hover:border-indigo-200 dark:hover:border-indigo-900">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="block text-xs font-semibold text-zinc-500 dark:text-zinc-400">
            {label}
          </span>
          <div className="mt-1 text-3xl font-bold tracking-tight text-zinc-950 dark:text-white">
            {value}
          </div>
        </div>

        {Icon && (
          <div className={`rounded-lg p-2.5 ${iconBg} ${iconColor}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>

      {children}

      <div className="mt-3 flex items-center gap-1.5 text-sm font-medium text-zinc-500 dark:text-zinc-400">
        {subtitle}
      </div>
    </Card>
  );
}

