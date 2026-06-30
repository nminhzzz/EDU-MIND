"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, BookOpen, FileText, ExternalLink } from "lucide-react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";

interface Classroom {
  id: number;
  teacher_id: number;
  subject_id: number;
  class_name: string;
  class_code: string;
  description: string | null;
}

interface Document {
  id: number;
  title: string;
  file_path: string;
  file_type: string;
  created_at: string;
}

interface ClassroomDetailModalProps {
  classroom: Classroom | null;
  onClose: () => void;
}

export function ClassroomDetailModal({ classroom, onClose }: ClassroomDetailModalProps) {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!classroom) return;
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get<Document[]>(`/documents/?subject_id=${classroom.subject_id}`);
        setDocs(res.data);
      } catch (err) {
        toast.error("Không thể tải tài liệu của lớp.");
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, [classroom]);

  return (
    <AnimatePresence>
      {classroom && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-45"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-xl p-8 max-h-[85vh] overflow-y-auto text-left">
              <div className="flex items-center justify-between mb-6 pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <div>
                  <h2 className="text-lg font-black text-zinc-900 dark:text-white">{classroom.class_name}</h2>
                  <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md inline-block mt-1">
                    {classroom.class_code}
                  </span>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-650 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {classroom.description && (
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">Giới thiệu lớp</span>
                    <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
                      {classroom.description}
                    </p>
                  </div>
                )}

                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5 text-indigo-500" />
                    Tài liệu môn học học tập
                  </span>

                  {loading ? (
                    <div className="py-6 text-center text-xs font-mono text-zinc-400">Đang đồng bộ tài liệu từ kho...</div>
                  ) : docs.length === 0 ? (
                    <div className="py-6 text-center text-xs text-zinc-400 dark:text-zinc-500 border border-dashed border-zinc-200 dark:border-zinc-850 rounded-xl">
                      Giáo viên chưa chia sẻ tài liệu nào cho môn học này.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {docs.map((doc) => (
                        <div
                          key={doc.id}
                          className="flex items-center justify-between p-3 border border-zinc-100 dark:border-zinc-800/80 rounded-xl bg-zinc-50/40 dark:bg-zinc-950/20"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                              <FileText className="w-4 h-4" />
                            </div>
                            <div>
                              <h4 className="text-xs font-bold text-zinc-800 dark:text-zinc-200">{doc.title}</h4>
                              <span className="text-[9px] text-zinc-400 uppercase font-bold">{doc.file_type}</span>
                            </div>
                          </div>
                          <a
                            href={doc.file_path}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 rounded-lg text-zinc-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-white dark:hover:bg-zinc-800 transition-colors shadow-sm"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
