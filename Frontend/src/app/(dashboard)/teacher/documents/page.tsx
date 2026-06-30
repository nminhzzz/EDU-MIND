"use client";

import React, { useEffect, useState, useRef } from "react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, X, FolderOpen } from "lucide-react";
import { DocumentRow } from "@/components/teacher/document-row";
import { EmptyState } from "@/components/teacher/empty-state";

interface Document {
  id: number;
  title: string;
  file_path: string;
  file_type: string;
  subject_id: number;
  created_by: number;
  created_at: string;
}

interface Subject {
  id: number;
  name: string;
  code: string;
}

export default function TeacherDocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const fetchData = async () => {
    try {
      const [docRes, subjRes] = await Promise.all([
        apiClient.get<Document[]>("/documents/"),
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
      });
      toast.success("Tải tài liệu lên thành công!");
      setShowModal(false);
      setTitle("");
      setSubjectId("");
      setFile(null);
      fetchData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Tải tài liệu thất bại.");
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
      toast.error(err?.response?.data?.detail || "Xóa tài liệu thất bại.");
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Đang tải danh sách tài liệu...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white">Kho Tài liệu Giảng dạy</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Tải lên và quản lý tài liệu cho các môn học. AI sẽ tự động phân tích nội dung để hỗ trợ sinh đề.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 active:scale-[0.98] transition-all flex items-center gap-2 cursor-pointer"
        >
          <Upload className="w-4 h-4" />
          Tải tài liệu
        </button>
      </div>

      {/* Documents list */}
      {documents.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title="Chưa có tài liệu nào"
          description="Hãy tải lên tài liệu giảng dạy đầu tiên để AI có thể hỗ trợ soạn đề thi."
        />
      ) : (
        <div className="space-y-3">
          {documents.map((doc, idx) => (
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
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-lg p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-black text-zinc-900 dark:text-white">Tải tài liệu mới</h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
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
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
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
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Chọn tệp *</label>
                    <div
                      onClick={() => fileRef.current?.click()}
                      className="w-full px-4 py-6 border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-xl bg-zinc-50 dark:bg-zinc-800/50 text-center cursor-pointer hover:border-violet-400 dark:hover:border-violet-600 transition-colors"
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
                    className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-[0.98] cursor-pointer"
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
