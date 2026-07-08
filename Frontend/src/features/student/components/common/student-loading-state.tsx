"use client";

import React from "react";
import { motion } from "framer-motion";

interface StudentLoadingStateProps {
  message: string;
  className?: string;
  messageClassName?: string;
  animated?: boolean;
  motionKey?: string;
}

export function StudentLoadingState({
  message,
  className = "",
  messageClassName = "text-sm font-medium text-zinc-500 dark:text-zinc-400",
  animated = false,
  motionKey = "loading",
}: StudentLoadingStateProps) {
  const content = (
    <div className={`py-24 text-center space-y-4 ${className}`.trim()}>
      <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
      <p className={messageClassName}>{message}</p>
    </div>
  );

  if (!animated) {
    return content;
  }

  return (
    <motion.div
      key={motionKey}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {content}
    </motion.div>
  );
}
