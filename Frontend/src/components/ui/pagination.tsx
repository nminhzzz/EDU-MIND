"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./button";

interface PaginationProps {
  page: number;
  pageSize: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  itemLabel?: string;
}

export function Pagination({ page, pageSize, totalItems, onPageChange, itemLabel = "mục" }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const currentPage = Math.min(Math.max(page, 1), totalPages);
  if (totalItems <= pageSize) return null;

  const start = (currentPage - 1) * pageSize + 1;
  const end = Math.min(currentPage * pageSize, totalItems);

  return (
    <div className="flex flex-col gap-3 border-t border-zinc-100 pt-4 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        Hiển thị <span className="font-semibold text-zinc-800 dark:text-zinc-200">{start}–{end}</span> trong {totalItems} {itemLabel}
      </p>
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" disabled={currentPage === 1} onClick={() => onPageChange(currentPage - 1)} aria-label="Trang trước">
          <ChevronLeft className="size-4" /><span className="hidden sm:inline">Trước</span>
        </Button>
        <span className="min-w-20 text-center text-sm font-semibold text-zinc-700 dark:text-zinc-300">{currentPage}/{totalPages}</span>
        <Button variant="secondary" size="sm" disabled={currentPage === totalPages} onClick={() => onPageChange(currentPage + 1)} aria-label="Trang sau">
          <span className="hidden sm:inline">Sau</span><ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
