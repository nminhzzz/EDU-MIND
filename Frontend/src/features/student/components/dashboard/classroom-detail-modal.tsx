"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, BookOpen, FileText, ExternalLink } from "lucide-react";
import { documentService } from "@/features/student/services/document";
import type { Classroom } from "@/features/student/types";
import { openStudyDocument, studyDocumentOpenError } from "@/utils/open-document";
import { StudyDocument } from "@/types/document";
import { toast } from "sonner";

interface ClassroomDetailModalProps {
  classroom: Classroom | null;
  onClose: () => void;
}

export function ClassroomDetailModal({ classroom, onClose }: ClassroomDetailModalProps) {
  const [docs, setDocs] = useState<StudyDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [openingId, setOpeningId] = useState<number | null>(null);

  const handleOpenDoc = async (doc: StudyDocument) => {
    setOpeningId(doc.id);
    try {
      await openStudyDocument(doc.id);
    } catch (err: unknown) {
      toast.error(studyDocumentOpenError(err, "Không thể mở tài liệu."));
    } finally {
      setOpeningId(null);
    }
  };

  useEffect(() => {
    if (!classroom) return;
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const res = await documentService.listBySubject(classroom.subject_id);
        setDocs(res.data);
      } catch {
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
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md shadow-2xl w-full max-w-xl p-8 max-h-[90vh] overflow-y-auto text-left">
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <div>
                  <h2 className="text-lg font-black text-sky-950 dark:text-white">{classroom.class_name}</h2>
                  <span className="text-xs font-mono font-bold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-900/60 px-2.5 py-0.5 rounded-md inline-block mt-1 border border-sky-200 dark:border-sky-800">
                    {classroom.class_code}
                  </span>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-md text-sky-400 hover:text-sky-700 dark:hover:text-white hover:bg-sky-50 dark:hover:bg-sky-900 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {classroom.description && (
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold text-sky-700/80 dark:text-sky-300/80 uppercase tracking-wider block">
                      Giới thiệu lớp
                    </span>
                    <p className="text-xs text-sky-900/80 dark:text-sky-300/80 leading-relaxed font-medium">
                      {classroom.description}
                    </p>
                  </div>
                )}

                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-sky-700/80 dark:text-sky-300/80 uppercase tracking-wider block flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5 text-sky-500" />
                    Tài liệu môn học
                  </span>

                  {loading ? (
                    <div className="py-6 text-center text-xs font-mono text-sky-600/70">
                      Đang đồng bộ tài liệu từ kho...
                    </div>
                  ) : docs.length === 0 ? (
                    <div className="py-6 text-center text-xs text-sky-800/70 dark:text-sky-300/70 border border-dashed border-sky-200 dark:border-sky-800 rounded-md">
                      Giáo viên chưa chia sẻ tài liệu nào cho môn học này.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {docs.map((doc) => (
                        <div
                          key={doc.id}
                          className="flex items-center justify-between p-3 border border-sky-100 dark:border-sky-900/60 rounded-md bg-sky-50/40 dark:bg-sky-950/30"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-md bg-sky-50 dark:bg-sky-900/50 text-sky-600 dark:text-sky-300 flex items-center justify-center border border-sky-200/60 dark:border-sky-800">
                              <FileText className="w-4 h-4" />
                            </div>
                            <div>
                              <h4 className="text-xs font-bold text-sky-950 dark:text-sky-100">{doc.title}</h4>
                              <span className="text-[9px] text-sky-600/80 dark:text-sky-400 uppercase font-bold">{doc.file_type}</span>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleOpenDoc(doc)}
                            disabled={openingId === doc.id}
                            className="p-1.5 rounded-md text-sky-400 hover:text-sky-700 dark:hover:text-white hover:bg-sky-50 dark:hover:bg-sky-900 transition-colors shadow-xs disabled:opacity-50"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </button>
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
