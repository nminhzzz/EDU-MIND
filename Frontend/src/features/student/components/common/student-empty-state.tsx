"use client";

import React from "react";
import { LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StudentEmptyStateAction {
  label: string;
  onClick: () => void;
}

interface StudentEmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  variant?: "card" | "center";
  action?: StudentEmptyStateAction;
  animated?: boolean;
  motionKey?: string;
}

export function StudentEmptyState({
  icon: Icon,
  title,
  description,
  variant = "card",
  action,
  animated = false,
  motionKey = "empty",
}: StudentEmptyStateProps) {
  const content =
    variant === "center" ? (
      <div className="flex-1 flex flex-col items-center justify-center text-zinc-400 space-y-4">
        <Icon className="w-16 h-16 opacity-20 text-indigo-400" />
        <div className="text-center space-y-1.5">
          <h3 className="text-sm font-bold text-zinc-700 dark:text-zinc-300">{title}</h3>
          <p className="text-xs text-zinc-400 max-w-xs">{description}</p>
        </div>
        {action && (
          <button
            onClick={action.onClick}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all active:scale-[0.98] cursor-pointer"
          >
            {action.label}
          </button>
        )}
      </div>
    ) : (
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-12 rounded-2xl text-center shadow-sm space-y-4">
        <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mx-auto">
          <Icon className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-250">{title}</h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-md mx-auto leading-relaxed">
            {description}
          </p>
        </div>
        {action && (
          <button
            onClick={action.onClick}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all active:scale-[0.98] cursor-pointer"
          >
            {action.label}
          </button>
        )}
      </div>
    );

  if (!animated) {
    return content;
  }

  return (
    <motion.div
      key={motionKey}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      {content}
    </motion.div>
  );
}
