import React from "react";
import { AlertCircle, Inbox } from "lucide-react";
import { Button } from "./button";

export function Skeleton({ className = "h-4 w-full" }: { className?: string }) {
  return <div aria-hidden className={`animate-pulse rounded-lg bg-zinc-200/80 dark:bg-zinc-800 ${className}`} />;
}

interface StateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, description, actionLabel, onAction }: StateProps) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center rounded-xl border border-dashed border-zinc-300 p-6 text-center dark:border-zinc-700">
      <Inbox className="mb-3 size-8 text-zinc-400" />
      <h3 className="text-base font-semibold text-zinc-900 dark:text-white">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-zinc-500 dark:text-zinc-400">{description}</p>
      {actionLabel && onAction && <Button className="mt-4" size="sm" onClick={onAction}>{actionLabel}</Button>}
    </div>
  );
}

export function ErrorState({ title, description, actionLabel = "Thử lại", onAction }: StateProps) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center rounded-xl border border-rose-200 bg-rose-50/50 p-6 text-center dark:border-rose-900 dark:bg-rose-950/20">
      <AlertCircle className="mb-3 size-8 text-rose-500" />
      <h3 className="text-base font-semibold text-zinc-900 dark:text-white">{title}</h3>
      <p className="mt-1 max-w-md text-sm text-zinc-600 dark:text-zinc-400">{description}</p>
      {onAction && <Button className="mt-4" size="sm" variant="secondary" onClick={onAction}>{actionLabel}</Button>}
    </div>
  );
}
