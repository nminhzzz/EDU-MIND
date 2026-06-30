"use client";
import React from "react";
import { LucideIcon } from "lucide-react";
import Link from "next/link";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
}

export function EmptyState({ icon: Icon, title, description, actionLabel, actionHref }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-2xl bg-violet-50 dark:bg-violet-950/30 text-violet-400 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-bold text-zinc-700 dark:text-zinc-300">{title}</h3>
      <p className="text-sm text-zinc-400 dark:text-zinc-500 mt-1 max-w-sm">{description}</p>
      {actionLabel && actionHref && (
        <Link
          href={actionHref}
          className="mt-5 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white text-sm font-bold rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-[0.98]"
        >
          {actionLabel}
        </Link>
      )}
    </div>
  );
}
