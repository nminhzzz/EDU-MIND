"use client";
import React, { useState } from "react";
import { FileText, Trash2, ExternalLink, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { openStudyDocument, studyDocumentOpenError } from "@/utils/open-document";
import { toast } from "sonner";

interface DocumentRowProps {
  id: number;
  title: string;
  fileType: string;
  filePath: string;
  createdAt: string;
  onDelete: (id: number) => void;
  index?: number;
}

const fileTypeColors: Record<string, string> = {
  pdf: "text-red-500 bg-red-50 dark:bg-red-950/30",
  doc: "text-blue-500 bg-blue-50 dark:bg-blue-950/30",
  docx: "text-blue-500 bg-blue-50 dark:bg-blue-950/30",
  txt: "text-zinc-500 bg-zinc-100 dark:bg-zinc-800",
  md: "text-emerald-500 bg-emerald-50 dark:bg-emerald-950/30",
};

export function DocumentRow({ id, title, fileType, filePath, createdAt, onDelete, index = 0 }: DocumentRowProps) {
  const colorClass = fileTypeColors[fileType] || "text-zinc-500 bg-zinc-100 dark:bg-zinc-800";
  const [opening, setOpening] = useState(false);

  const handleView = async () => {
    setOpening(true);
    try {
      await openStudyDocument(id);
    } catch (err: unknown) {
      toast.error(studyDocumentOpenError(err, "Không thể mở tài liệu."));
    } finally {
      setOpening(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group flex items-center gap-4 p-4 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-900 hover:border-violet-300 dark:hover:border-violet-700 transition-colors"
    >
      <div className={`w-10 h-10 flex items-center justify-center rounded-lg ${colorClass}`}>
        <FileText className="w-5 h-5" />
      </div>
      <div className="flex-1 min-w-0">
        <button
          type="button"
          onClick={handleView}
          disabled={opening}
          className="text-left w-full group/title cursor-pointer disabled:cursor-wait"
        >
          <h4 className="text-sm font-bold text-zinc-800 dark:text-zinc-200 truncate group-hover/title:text-violet-600 dark:group-hover/title:text-violet-400 transition-colors">
            {title}
          </h4>
          <span className="text-xs text-zinc-400 dark:text-zinc-500">
            {fileType.toUpperCase()} • {new Date(createdAt).toLocaleDateString("vi-VN")}
          </span>
        </button>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={handleView}
          disabled={opening}
          className="p-2 rounded-lg text-zinc-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-950/40 transition-colors cursor-pointer disabled:opacity-50"
          title="Xem tài liệu"
        >
          {opening ? <Loader2 className="w-4 h-4 animate-spin" /> : <ExternalLink className="w-4 h-4" />}
        </button>
        <button
          onClick={() => onDelete(id)}
          className="p-2 rounded-lg text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors cursor-pointer"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
}
