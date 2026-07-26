"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  BrainCircuit,
  Loader2,
  Award,
  BookOpen,
  Edit3,
  Save,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { toast } from "sonner";
import classroomApi, { StudentAnalyticData } from "@/services/classroom";

interface StudentAnalyticsModalProps {
  open: boolean;
  onClose: () => void;
  classroomId: number;
  studentId: number;
  studentName: string;
  subjectName?: string | null;
}

export function StudentAnalyticsModal({
  open,
  onClose,
  classroomId,
  studentId,
  studentName,
  subjectName,
}: StudentAnalyticsModalProps) {
  const [data, setData] = useState<StudentAnalyticData | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [feedbackInput, setFeedbackInput] = useState("");
  const [weakInput, setWeakInput] = useState("");
  const [strongInput, setStrongInput] = useState("");

  useEffect(() => {
    if (!open || !classroomId || !studentId) return;

    const fetchAnalytics = async () => {
      setLoading(true);
      setIsEditing(false);
      try {
        const res = await classroomApi.getStudentAnalytics(classroomId, studentId);
        const analytic = res.data;
        setData(analytic);
        setFeedbackInput(analytic.ai_feedback || "");
        setWeakInput(
          (analytic.weak_topics || []).map((t) => t.topic).join(", ")
        );
        setStrongInput(
          (analytic.strong_topics || []).map((t) => t.topic).join(", ")
        );
      } catch (err) {
        console.error("Lỗi lấy báo cáo học lực:", err);
        toast.error("Không thể tải báo cáo học lực của học sinh.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [open, classroomId, studentId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const weakList = weakInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((topic) => ({ topic }));

      const strongList = strongInput
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((topic) => ({ topic }));

      const res = await classroomApi.updateStudentAnalytics(
        classroomId,
        studentId,
        {
          ai_feedback: feedbackInput.trim() || null,
          weak_topics: weakList,
          strong_topics: strongList,
        }
      );

      setData(res.data);
      setIsEditing(false);
      toast.success("Đã cập nhật báo cáo đánh giá học sinh thành công!");
    } catch (err) {
      console.error("Lỗi cập nhật báo cáo:", err);
      toast.error("Không thể lưu đánh giá.");
    } finally {
      setSaving(false);
    }
  };

  const getScoreBadge = (score: number) => {
    if (score >= 8.0) {
      return { label: "Xuất sắc / Giỏi", color: "bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800" };
    }
    if (score >= 5.0) {
      return { label: "Khá / Trung bình", color: "bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800" };
    }
    return { label: "Cần cải thiện", color: "bg-rose-50 text-rose-600 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800" };
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-50"
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden text-left">
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-zinc-150 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/50 dark:bg-zinc-950/30 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-black text-sm shadow-md shadow-indigo-600/20">
                    {studentName ? studentName.charAt(0).toUpperCase() : "U"}
                  </div>
                  <div>
                    <h3 className="text-base font-black text-zinc-900 dark:text-white flex items-center gap-2">
                      {studentName}
                      {subjectName && (
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                          {subjectName}
                        </span>
                      )}
                    </h3>
                    <p className="text-[11px] font-medium text-zinc-400">
                      Báo cáo & Đánh giá năng lực học tập theo môn
                    </p>
                  </div>
                </div>

                <button
                  onClick={onClose}
                  className="p-1.5 rounded-xl hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Body */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {loading ? (
                  <div className="flex flex-col items-center justify-center py-20 gap-3 text-zinc-400">
                    <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                    <span className="text-xs font-semibold">Đang tổng hợp báo cáo học lực...</span>
                  </div>
                ) : !data ? (
                  <div className="text-center py-16 text-zinc-400 text-xs font-medium">
                    Không có dữ liệu báo cáo học lực cho học sinh này.
                  </div>
                ) : (
                  <>
                    {/* KPI Stat Cards */}
                    <div className="grid grid-cols-2 gap-4">
                      {/* Average Score Card */}
                      <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
                            Điểm trung bình môn
                          </span>
                          <Award className="w-4 h-4 text-indigo-500" />
                        </div>
                        <div className="flex items-baseline gap-2 pt-1">
                          <span className="text-2xl font-black text-zinc-900 dark:text-white">
                            {Number(data.average_score).toFixed(1)}
                          </span>
                          <span className="text-xs font-bold text-zinc-400">/ 10</span>
                        </div>
                        <span className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded-md border mt-1 ${getScoreBadge(Number(data.average_score)).color}`}>
                          {getScoreBadge(Number(data.average_score)).label}
                        </span>
                      </div>

                      {/* Quizzes Completed Card */}
                      <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
                            Số bài thi đã làm
                          </span>
                          <BookOpen className="w-4 h-4 text-indigo-500" />
                        </div>
                        <div className="flex items-baseline gap-2 pt-1">
                          <span className="text-2xl font-black text-zinc-900 dark:text-white">
                            {data.quizzes_completed}
                          </span>
                          <span className="text-xs font-bold text-zinc-400">bài test</span>
                        </div>
                        <span className="inline-block text-[10px] font-medium text-zinc-400 mt-1">
                          Tự động cập nhật từ các bài làm
                        </span>
                      </div>
                    </div>

                    {/* Form / Content View */}
                    <form onSubmit={handleSave} className="space-y-5">
                      {/* Weak & Strong Topics */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Strong Topics */}
                        <div className="p-4 rounded-xl border border-emerald-200/60 dark:border-emerald-950/40 bg-emerald-50/30 dark:bg-emerald-950/10 space-y-2">
                          <div className="flex items-center gap-1.5 text-xs font-black text-emerald-700 dark:text-emerald-400">
                            <CheckCircle2 className="w-4 h-4" />
                            Chủ đề Nắm vững (Điểm mạnh)
                          </div>
                          {isEditing ? (
                            <input
                              type="text"
                              value={strongInput}
                              onChange={(e) => setStrongInput(e.target.value)}
                              placeholder="Nhập các chủ đề phân cách bằng dấu phẩy..."
                              className="w-full p-2 text-xs border border-zinc-200 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-medium"
                            />
                          ) : (
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {data.strong_topics && data.strong_topics.length > 0 ? (
                                data.strong_topics.map((t, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 rounded-md border border-emerald-200 dark:border-emerald-900"
                                  >
                                    {t.topic}
                                  </span>
                                ))
                              ) : (
                                <span className="text-xs text-zinc-400 italic">Chưa xác định</span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Weak Topics */}
                        <div className="p-4 rounded-xl border border-rose-200/60 dark:border-rose-950/40 bg-rose-50/30 dark:bg-rose-950/10 space-y-2">
                          <div className="flex items-center gap-1.5 text-xs font-black text-rose-700 dark:text-rose-400">
                            <AlertTriangle className="w-4 h-4" />
                            Chủ đề Cần cải thiện (Điểm yếu)
                          </div>
                          {isEditing ? (
                            <input
                              type="text"
                              value={weakInput}
                              onChange={(e) => setWeakInput(e.target.value)}
                              placeholder="Nhập các chủ đề phân cách bằng dấu phẩy..."
                              className="w-full p-2 text-xs border border-zinc-200 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-rose-500 font-medium"
                            />
                          ) : (
                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {data.weak_topics && data.weak_topics.length > 0 ? (
                                data.weak_topics.map((t, idx) => (
                                  <span
                                    key={idx}
                                    className="px-2 py-0.5 text-[11px] font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 rounded-md border border-rose-200 dark:border-rose-900"
                                  >
                                    {t.topic}
                                  </span>
                                ))
                              ) : (
                                <span className="text-xs text-zinc-400 italic">Chưa ghi nhận</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* AI / Teacher Evaluation Feedback */}
                      <div className="space-y-2 pt-1">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5 text-xs font-black text-zinc-800 dark:text-zinc-200">
                            <BrainCircuit className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                            Đánh giá & Nhận xét năng lực
                          </div>
                          {!isEditing && (
                            <button
                              type="button"
                              onClick={() => setIsEditing(true)}
                              className="flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 px-2 py-1 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/30 transition-colors cursor-pointer"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                              Chỉnh sửa nhận xét
                            </button>
                          )}
                        </div>

                        {isEditing ? (
                          <div className="space-y-2">
                            <textarea
                              rows={5}
                              value={feedbackInput}
                              onChange={(e) => setFeedbackInput(e.target.value)}
                              placeholder="Nhập nội dung nhận xét đánh giá học sinh..."
                              className="w-full p-3 text-xs border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-800 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-medium leading-relaxed resize-none"
                            />
                            <p className="text-[10px] text-zinc-400 italic">
                              * Nhận xét bạn nhập ở đây sẽ đè nội dung hiển thị cho học sinh trong hồ sơ học tập.
                            </p>
                          </div>
                        ) : (
                          <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50/60 dark:bg-zinc-950/40 text-xs leading-relaxed text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap font-medium">
                            {data.ai_feedback ? (
                              data.ai_feedback
                            ) : (
                              <span className="text-zinc-400 italic">
                                Chưa có nhận xét đánh giá. Bấm "Chỉnh sửa nhận xét" để thêm đánh giá cho học sinh.
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Action Controls in Edit Mode */}
                      {isEditing && (
                        <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-150 dark:border-zinc-800">
                          <button
                            type="button"
                            onClick={() => {
                              setIsEditing(false);
                              setFeedbackInput(data.ai_feedback || "");
                              setWeakInput(
                                (data.weak_topics || []).map((t) => t.topic).join(", ")
                              );
                              setStrongInput(
                                (data.strong_topics || []).map((t) => t.topic).join(", ")
                              );
                            }}
                            className="px-4 py-2 rounded-xl text-xs font-bold text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                          >
                            Hủy
                          </button>
                          <button
                            type="submit"
                            disabled={saving}
                            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/20 flex items-center gap-1.5 transition-colors cursor-pointer disabled:opacity-50"
                          >
                            {saving ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Save className="w-4 h-4" />
                            )}
                            Lưu đánh giá
                          </button>
                        </div>
                      )}
                    </form>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
