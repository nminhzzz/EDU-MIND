"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, X, GraduationCap } from "lucide-react";
import { ClassroomCard } from "@/components/teacher/classroom-card";
import { EmptyState } from "@/components/teacher/empty-state";

interface Classroom {
  id: number;
  teacher_id: number;
  subject_id: number;
  class_name: string;
  class_code: string;
  description: string | null;
  created_at: string;
}

interface Subject {
  id: number;
  name: string;
  code: string;
}

export default function TeacherClassroomsPage() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    subject_id: "",
    class_name: "",
    class_code: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      const [clsRes, subjRes] = await Promise.all([
        apiClient.get<Classroom[]>("/classrooms/"),
        apiClient.get<Subject[]>("/subjects/"),
      ]);
      setClassrooms(clsRes.data);
      setSubjects(subjRes.data);
    } catch (err) {
      toast.error("Không thể tải danh sách lớp học.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.subject_id || !formData.class_name || !formData.class_code) {
      toast.error("Vui lòng điền đầy đủ thông tin bắt buộc.");
      return;
    }
    setSubmitting(true);
    try {
      await apiClient.post("/classrooms/", {
        ...formData,
        subject_id: parseInt(formData.subject_id),
      });
      toast.success("Tạo lớp học thành công!");
      setShowModal(false);
      setFormData({ subject_id: "", class_name: "", class_code: "", description: "" });
      fetchData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Tạo lớp học thất bại.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Đang tải danh sách lớp học...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white">Quản lý Lớp học</h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Tạo mới, quản lý và theo dõi tiến độ các lớp học bạn đang phụ trách.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 active:scale-[0.98] transition-all flex items-center gap-2 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          Tạo lớp mới
        </button>
      </div>

      {/* Classrooms grid */}
      {classrooms.length === 0 ? (
        <EmptyState
          icon={GraduationCap}
          title="Chưa có lớp học nào"
          description="Hãy tạo lớp học đầu tiên của bạn để bắt đầu quản lý và giảng dạy."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {classrooms.map((cls, idx) => (
            <ClassroomCard
              key={cls.id}
              id={cls.id}
              className_={cls.class_name}
              classCode={cls.class_code}
              studentCount={0}
              subjectId={cls.subject_id}
              index={idx}
            />
          ))}
        </div>
      )}

      {/* Modal */}
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
                  <h2 className="text-xl font-black text-zinc-900 dark:text-white">Tạo lớp học mới</h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleCreate} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Môn học *</label>
                    <select
                      value={formData.subject_id}
                      onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    >
                      <option value="">-- Chọn môn học --</option>
                      {subjects.map((s) => (
                        <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Tên lớp *</label>
                    <input
                      type="text"
                      value={formData.class_name}
                      onChange={(e) => setFormData({ ...formData, class_name: e.target.value })}
                      placeholder="VD: Lớp Lập trình Java K10"
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Mã lớp (duy nhất) *</label>
                    <input
                      type="text"
                      value={formData.class_code}
                      onChange={(e) => setFormData({ ...formData, class_code: e.target.value.toUpperCase() })}
                      placeholder="VD: JAVA-K10-01"
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm font-mono focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">Mô tả</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Mô tả ngắn gọn về lớp học..."
                      rows={3}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none resize-none"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-[0.98] cursor-pointer"
                  >
                    {submitting ? "Đang tạo..." : "Tạo lớp học"}
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
