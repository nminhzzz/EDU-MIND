"use client";

import React, { useEffect, useState, useRef } from "react";
import { apiClient } from "@/services/api-client";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X, FolderOpen } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { DocumentRow } from "@/components/teacher/document-row";
import { EmptyState } from "@/components/teacher/empty-state";
import { StudyDocument } from "@/types/document";
import { Subject } from "@/types/subject";
import { Button, PageHeader, Skeleton } from "@/components/ui";

export default function TeacherDocumentsPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<StudyDocument[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [filterType, setFilterType] = useState<"mine" | "all">("mine");
  const [title, setTitle] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchData = async () => {
    try {
      const [docRes, subjRes] = await Promise.all([
        apiClient.get<StudyDocument[]>("/documents/"),
        apiClient.get<Subject[]>("/subjects/"),
      ]);
      setDocuments(docRes.data);
      setSubjects(subjRes.data);
    } catch (err) {
      toast.error("Không thể tải danh sách tài liệu.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredDocuments = documents.filter((doc) => {
    if (filterType === "mine") {
      return doc.created_by === user?.id;
    }
    return true;
  });

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId || !title || !file) {
      toast.error("Vui lòng điền đầy đủ thông tin và chọn tệp.");
      return;
    }
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append("subject_id", subjectId);
      fd.append("title", title);
      fd.append("file", file);
      await apiClient.post("/documents/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60_000,
      });
      toast.success("Tải tài liệu lên thành công! AI đang phân tích nội dung trong nền.");
      setShowModal(false);
      setTitle("");
      setSubjectId("");
      setFile(null);
      fetchData();
    } catch (err: any) {
      toast.error(parseApiError(err, "Tải tài liệu thất bại."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa tài liệu này?")) return;
    try {
      await apiClient.delete(`/documents/${docId}`);
      toast.success("Đã xóa tài liệu thành công.");
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err: any) {
      toast.error(parseApiError(err, "Xóa tài liệu thất bại."));
    }
  };

  if (loading) {
    return <div className="space-y-5"><Skeleton className="h-20" /><Skeleton className="h-12" /><Skeleton className="h-72" /></div>;
  }

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Không gian giáo viên" title="Kho tài liệu giảng dạy" description="Quản lý nguồn học liệu để AI hỗ trợ tạo nội dung và đề kiểm tra." actions={<Button onClick={() => setShowModal(true)}><Upload className="size-4" /> Tải tài liệu</Button>} />

      {/* Tabs Filter */}
      <div className="flex border-b border-zinc-200 dark:border-zinc-800 gap-6">
        <button
          onClick={() => setFilterType("mine")}
          className={`pb-3 text-sm font-bold relative transition-colors ${
            filterType === "mine"
              ? "text-violet-600 dark:text-violet-400 font-extrabold"
              : "text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300"
          }`}
        >
          Tài liệu của tôi
          {filterType === "mine" && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-600 dark:bg-violet-400"
            />
          )}
        </button>
        <button
          onClick={() => setFilterType("all")}
          className={`pb-3 text-sm font-bold relative transition-colors ${
            filterType === "all"
              ? "text-violet-600 dark:text-violet-400 font-extrabold"
              : "text-zinc-400 dark:text-zinc-500 hover:text-zinc-600 dark:hover:text-zinc-300"
          }`}
        >
          Tất cả tài liệu
          {filterType === "all" && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-600 dark:bg-violet-400"
            />
          )}
        </button>
      </div>

      {/* Documents list */}
      {filteredDocuments.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title={filterType === "mine" ? "Bạn chưa có tài liệu nào" : "Chưa có tài liệu nào"}
          description={
            filterType === "mine"
              ? "Hãy tải lên tài liệu giảng dạy đầu tiên của bạn để AI hỗ trợ soạn đề thi."
              : "Không tìm thấy tài liệu nào từ tất cả các giáo viên."
          }
        />
      ) : (
        <div className="space-y-3">
          {filteredDocuments.map((doc, idx) => (
            <DocumentRow
              key={doc.id}
              id={doc.id}
              title={doc.title}
              fileType={doc.file_type}
              filePath={doc.file_path}
              createdAt={doc.created_at}
              onDelete={handleDelete}
              index={idx}
            />
          ))}
        </div>
      )}

      {/* Upload Modal */}
      <AnimatePresence>
        {showModal && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowModal(false)}
              className="fixed inset-0 bg-black z-40"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
            >
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-md shadow-2xl w-full max-w-lg p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-black text-zinc-900 dark:text-white">Tải tài liệu mới</h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-md text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleUpload} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Môn học *</label>
                    <select
                      value={subjectId}
                      onChange={(e) => setSubjectId(e.target.value)}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    >
                      <option value="">-- Chọn môn học --</option>
                      {subjects.map((s) => (
                        <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Tiêu đề tài liệu *</label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="VD: Giáo trình Đại số tuyến tính Chương 3"
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Chọn tệp *</label>
                    <div
                      onClick={() => fileRef.current?.click()}
                      className="w-full px-4 py-6 border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-md bg-zinc-50 dark:bg-zinc-800/50 text-center cursor-pointer hover:border-violet-400 dark:hover:border-violet-600 transition-colors"
                    >
                      <Upload className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mx-auto mb-2" />
                      <p className="text-sm text-zinc-500 dark:text-zinc-400">
                        {file ? file.name : "Nhấp để chọn tệp (PDF, DOCX, TXT, MD...)"}
                      </p>
                    </div>
                    <input
                      ref={fileRef}
                      type="file"
                      onChange={(e) => setFile(e.target.files?.[0] || null)}
                      className="hidden"
                      accept=".pdf,.doc,.docx,.txt,.md,.json,.csv,.html"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-sm rounded-md shadow-md shadow-violet-500/20 transition-all active:scale-[0.98] cursor-pointer"
                  >
                    {submitting ? "Đang tải lên..." : "Tải tài liệu lên"}
                  </button>
                </form>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
