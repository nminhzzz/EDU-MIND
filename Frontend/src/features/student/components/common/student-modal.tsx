"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

type StudentModalMaxWidth = "md" | "lg" | "5xl";

const maxWidthClasses: Record<StudentModalMaxWidth, string> = {
  md: "max-w-md",
  lg: "max-w-lg",
  "5xl": "max-w-5xl",
};

interface StudentModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  children: React.ReactNode;
  maxWidth?: StudentModalMaxWidth;
  overlayZIndex?: "z-40" | "z-45";
  panelClassName?: string;
  contentClassName?: string;
  animation?: { scale?: number; y?: number };
  withAnimatePresence?: boolean;
  showCloseButton?: boolean;
}

export function StudentModal({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = "md",
  overlayZIndex = "z-45",
  panelClassName = "",
  contentClassName = "p-8 text-left",
  animation = { scale: 0.95, y: 20 },
  withAnimatePresence = true,
  showCloseButton = true,
}: StudentModalProps) {
  const panelZIndex = overlayZIndex === "z-40" ? "z-50" : "z-50";

  const modalContent = isOpen ? (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className={`fixed inset-0 bg-black ${overlayZIndex}`}
      />
      <motion.div
        initial={{ opacity: 0, scale: animation.scale ?? 0.95, y: animation.y ?? 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: animation.scale ?? 0.95, y: animation.y ?? 20 }}
        className={`fixed inset-0 ${panelZIndex} flex items-center justify-center p-4 ${panelClassName}`.trim()}
      >
        <div
          className={`bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full ${maxWidthClasses[maxWidth]} ${contentClassName}`.trim()}
        >
          {title !== undefined && (
            <div className="flex items-center justify-between mb-6">
              {typeof title === "string" ? (
                <h2 className="text-xl font-black text-zinc-900 dark:text-white">{title}</h2>
              ) : (
                title
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-650 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}
          {children}
        </div>
      </motion.div>
    </>
  ) : null;

  if (!withAnimatePresence) {
    return modalContent;
  }

  return <AnimatePresence>{modalContent}</AnimatePresence>;
}
