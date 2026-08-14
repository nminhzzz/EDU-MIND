import React from "react";
import { cn } from "@/utils/cn";

export function TabsList({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div role="tablist" className={cn("inline-flex rounded-lg border border-zinc-200 bg-zinc-100 p-1 dark:border-zinc-800 dark:bg-zinc-900", className)} {...props} />;
}

interface TabButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> { active?: boolean }
export function TabButton({ active, className, ...props }: TabButtonProps) {
  return <button role="tab" aria-selected={active} className={cn("rounded-md px-3 py-2 text-sm font-medium text-zinc-500 transition-colors hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white", active && "bg-white text-zinc-950 shadow-sm dark:bg-zinc-800 dark:text-white", className)} {...props} />;
}
