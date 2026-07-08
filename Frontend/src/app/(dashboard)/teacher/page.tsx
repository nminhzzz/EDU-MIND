"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { motion } from "framer-motion";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import {
  Users,
  GraduationCap,
  FolderOpen,
  Plus,
  ChevronRight,
  ClipboardCheck,
} from "lucide-react";
import { StatCard } from "@/components/teacher/stat-card";
import { ClassroomCard } from "@/components/teacher/classroom-card";
import { EmptyState } from "@/components/teacher/empty-state";
import { Classroom } from "@/types/classroom";
import { StudyDocument } from "@/types/document";
import { recommendationApi } from "@/services/recommendation";

export default function TeacherDashboard() {
  const { user, isLoading: authLoading } = useAuth();
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [documents, setDocuments] = useState<StudyDocument[]>([]);
  const [pendingReviews, setPendingReviews] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;

    const fetchData = async () => {
      try {
        const [clsRes, docRes, pendingRes] = await Promise.all([
          apiClient.get<Classroom[]>("/classrooms/"),
          apiClient.get<StudyDocument[]>("/documents/"),
          recommendationApi.getPendingReviews(),
        ]);
        setClassrooms(clsRes.data);
        setDocuments(docRes.data);
        setPendingReviews(pendingRes.data.length);
      } catch (err) {
        console.error("Lỗi tải dữ liệu dashboard giáo viên:", err);
        toast.error("Không thể tải dữ liệu. Vui lòng thử lại.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [authLoading]);

  if (authLoading || loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Đang tải dữ liệu...</p>
      </div>
    );
  }

  const totalStudents = classrooms.reduce(
    (sum, cls) => sum + (cls.student_count ?? 0),
    0,
  );

  const stats = [
    {
      label: "Lớp học phụ trách",
      value: classrooms.length,
      icon: GraduationCap,
      color: "text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/30",
    },
    {
      label: "Tài liệu giảng dạy",
      value: documents.length,
      icon: FolderOpen,
      color: "text-pink-600 dark:text-pink-400 bg-pink-50 dark:bg-pink-950/30",
    },
    {
      label: "Học sinh quản lý",
      value: totalStudents,
      icon: Users,
      color: "text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/30",
    },
  ];

  return (
    <div className="space-y-6">
      {/* 1. Welcome banner */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-8 shadow-sm rounded-xl"
      >
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center font-bold text-xl rounded-xl">
            EM
          </div>
          <div>
            <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
              Chào mừng, {user?.full_name || "Giáo viên"}!
            </h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              Hệ thống trợ lý giáo án RAG và chấm điểm thi bằng AI đã sẵn sàng phục vụ.
            </p>
          </div>
        </div>
        <Link
          href={ROUTES.TEACHER_DOCUMENTS}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer w-fit"
        >
          <Plus className="w-4 h-4" />
          Soạn đề & Tài liệu
        </Link>
      </motion.div>

      {/* 2. Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {stats.map((stat, idx) => (
          <StatCard key={stat.label} {...stat} index={idx} />
        ))}
        <StatCard
          label="Đề xuất chờ duyệt"
          value={pendingReviews}
          icon={ClipboardCheck}
          color="text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30"
          index={3}
        />
      </div>

      {pendingReviews > 0 && (
        <Link
          href={ROUTES.TEACHER_RECOMMENDATIONS}
          className="flex items-center justify-between gap-4 p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-xl hover:border-amber-300 dark:hover:border-amber-700 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <ClipboardCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-bold text-amber-800 dark:text-amber-300">
                {pendingReviews} đề xuất ôn tập AI đang chờ duyệt
              </p>
              <p className="text-xs text-amber-600/80 dark:text-amber-400/80 mt-0.5">
                Học sinh cần bạn xem xét trước khi nhận gợi ý ôn tập
              </p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
        </Link>
      )}

      {/* 3. Classrooms & AI Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Classrooms */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-6 shadow-sm rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800 mb-4">
              <h2 className="font-extrabold text-lg text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                Lớp học đang phụ trách
              </h2>
              <span className="text-xs font-mono text-zinc-400 dark:text-zinc-500">{classrooms.length} lớp</span>
            </div>

            {classrooms.length === 0 ? (
              <EmptyState
                icon={GraduationCap}
                title="Chưa có lớp học nào"
                description="Bạn chưa tạo hoặc chưa được phân công lớp học. Hãy tạo lớp học đầu tiên!"
                actionLabel="Tạo lớp học"
                actionHref={ROUTES.TEACHER_CLASSROOMS}
              />
            ) : (
              <div className="space-y-3">
                {classrooms.slice(0, 4).map((cls, idx) => (
                  <ClassroomCard
                    key={cls.id}
                    id={cls.id}
                    className_={cls.class_name}
                    classCode={cls.class_code}
                    studentCount={cls.student_count ?? 0}
                    subjectId={cls.subject_id}
                    index={idx}
                  />
                ))}
              </div>
            )}
          </div>

          {classrooms.length > 0 && (
            <div className="pt-6 border-t border-zinc-100 dark:border-zinc-800 mt-6 flex justify-end">
              <Link
                href={ROUTES.TEACHER_CLASSROOMS}
                className="text-xs font-bold text-violet-600 dark:text-violet-400 hover:underline flex items-center gap-1"
              >
                Quản lý toàn bộ danh sách lớp
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}
        </div>

        {/* Right: HITL Recommendations Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800 text-white p-8 shadow-sm flex flex-col justify-between relative overflow-hidden rounded-xl"
        >
          <div className="absolute top-[-30%] right-[-30%] w-48 h-48 rounded-full bg-violet-500/10 blur-2xl pointer-events-none" />
          <div>
            <div className="w-12 h-12 bg-white/5 text-violet-400 border border-zinc-800 flex items-center justify-center mb-6 rounded-xl">
              <ClipboardCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-extrabold tracking-tight">Duyệt đề xuất AI</h3>
            <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
              Học sinh làm bài dưới 8 điểm sẽ nhận gợi ý ôn tập từ AI. Bạn xem xét và phê duyệt trước khi gửi cho học sinh.
            </p>
          </div>
          <Link
            href={ROUTES.TEACHER_RECOMMENDATIONS}
            className="mt-8 px-5 py-3 bg-violet-600 hover:bg-violet-500 text-white font-extrabold text-sm text-center shadow-lg transition-transform active:scale-[0.98] cursor-pointer rounded-xl"
          >
            {pendingReviews > 0
              ? `Duyệt ${pendingReviews} đề xuất`
              : "Xem đề xuất ôn tập"}
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
