"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import { studyPlanApi, StudyPlan } from "@/services/study-plan";
import { motion, AnimatePresence } from "framer-motion";
import { TaskStudyModal } from "@/components/student/task-study-modal";
import { toast } from "sonner";
import { apiClient } from "@/services/api-client";
import { GraduationCap } from "lucide-react";
import { StudentWelcomeBanner } from "@/components/student/welcome-banner";
import { ClassroomJoinModal } from "@/components/student/classroom-join-modal";
import { ClassroomDetailModal } from "@/components/student/classroom-detail-modal";

interface Classroom {
  id: number;
  teacher_id: number;
  subject_id: number;
  class_name: string;
  class_code: string;
  description: string | null;
  created_at: string;
}

export default function StudentDashboard() {
  const { user } = useAuth();

  // 1. Quản lý trạng thái Realtime Stats từ SSE (/dashboard/stream)
  const [stats, setStats] = useState<any>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);

  // 2. Quản lý trạng thái Danh sách nhiệm vụ hôm nay từ API (/plans/)
  const [tasks, setTasks] = useState<StudyPlan[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);

  // 3. Quản lý danh sách lớp học đã tham gia
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [classroomsLoading, setClassroomsLoading] = useState(true);

  // 4. Quản lý Modal Gia nhập lớp & Xem chi tiết lớp
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [activeClassroom, setActiveClassroom] = useState<Classroom | null>(null);
  const [activeTask, setActiveTask] = useState<any | null>(null);

  // Lấy danh sách nhiệm vụ hôm nay từ API
  const fetchTodayTasks = async () => {
    try {
      const todayStr = new Date().toISOString().split("T")[0];
      const response = await studyPlanApi.getPlans({
        start_date: todayStr,
        end_date: todayStr,
      });
      setTasks(response.data);
    } catch (err) {
      console.error("Lỗi tải danh sách nhiệm vụ:", err);
    } finally {
      setTasksLoading(false);
    }
  };

  // Lấy danh sách lớp học học sinh đã gia nhập
  const fetchClassrooms = async () => {
    try {
      const response = await apiClient.get<Classroom[]>("/classrooms/");
      setClassrooms(response.data);
    } catch (err) {
      console.error("Lỗi tải danh sách lớp học:", err);
    } finally {
      setClassroomsLoading(false);
    }
  };

  // Mở kết nối SSE để đồng bộ realtime chỉ số từ Backend
  useEffect(() => {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const eventSource = new EventSource(`${baseUrl}/dashboard/stream`, {
      withCredentials: true,
    });

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.error) {
          setStatsError(parsed.error);
        } else {
          setStats(parsed);
          setStatsError(null);
        }
      } catch (err) {
        console.error("Lỗi phân tích cú pháp dữ liệu SSE:", err);
      } finally {
        setStatsLoading(false);
      }
    };

    eventSource.onerror = (err) => {
      console.error("EventSource gặp lỗi kết nối:", err);
      setStatsError("Mất kết nối đồng bộ dữ liệu thời gian thực.");
      setStatsLoading(false);
    };

    fetchTodayTasks();
    fetchClassrooms();

    return () => {
      eventSource.close();
    };
  }, []);

  // Xử lý thay đổi trạng thái hoàn thành của nhiệm vụ trực tiếp với API
  const handleToggleTaskStatus = async (task: StudyPlan) => {
    const newStatus = task.status === "done" ? "todo" : "done";

    // Cập nhật UI tạm thời (Optimistic UI Update)
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, status: newStatus } : t)),
    );

    try {
      await studyPlanApi.updatePlanStatus(task.id, newStatus);
      toast.success(`Đã cập nhật trạng thái nhiệm vụ.`);
      fetchTodayTasks();
    } catch (err) {
      console.error("Lỗi cập nhật trạng thái nhiệm vụ:", err);
      toast.error("Không thể cập nhật trạng thái nhiệm vụ.");
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: task.status } : t)),
      );
    }
  };

  const todayStrFormatted = new Date().toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  return (
    <div className="space-y-6 text-left">
      {/* 1. Lời chào mừng & Banner */}
      <StudentWelcomeBanner
        fullName={user?.full_name || "Học sinh"}
        onJoinClassClick={() => setShowJoinModal(true)}
      />

      {/* 2. Hàng chỉ số KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* GPA Card */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm transition-all hover:border-zinc-300 dark:hover:border-zinc-700"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Điểm trung bình
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {statsLoading
              ? "-- / 10"
              : `${stats?.quizzes?.avg_score || "0.0"} / 10`}
          </div>
          <span className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-2 block font-medium">
            Từ {stats?.quizzes?.total_attempts || 0} bài tập đã luyện tập.
          </span>
        </motion.div>

        {/* Lộ trình học tập */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.05 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm transition-all hover:border-zinc-300 dark:hover:border-zinc-700"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Tiến độ lộ trình
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {statsLoading ? "-- %" : `${stats?.overall?.progress_pct || 0}%`}
          </div>

          <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div
              className="bg-indigo-600 dark:bg-indigo-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats?.overall?.progress_pct || 0}%` }}
            />
          </div>

          <span className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-2 block font-medium">
            Đã xong {stats?.overall?.done_plans || 0} /{" "}
            {stats?.overall?.total_plans || 0} nhiệm vụ.
          </span>
        </motion.div>

        {/* Mục tiêu đang chạy */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm transition-all hover:border-zinc-300 dark:hover:border-zinc-700"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Mục tiêu hoạt động
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {statsLoading
              ? "-- mục tiêu"
              : `${stats?.active_goals || 0} đang chạy`}
          </div>
          <span className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-2 block font-medium">
            Có {stats?.unread_notifications || 0} thông báo chưa đọc.
          </span>
        </motion.div>
      </div>

      {/* 3. Lớp học của tôi */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800">
          <h2 className="font-extrabold text-sm text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-indigo-500" />
            Lớp học tôi đã tham gia
          </h2>
          <span className="text-xs font-mono text-zinc-400 dark:text-zinc-500">{classrooms.length} lớp đã gia nhập</span>
        </div>

        {classroomsLoading ? (
          <div className="py-8 text-center text-xs font-mono text-zinc-400">Đang tải danh sách lớp học...</div>
        ) : classrooms.length === 0 ? (
          <div className="py-8 text-center text-sm text-zinc-500 dark:text-zinc-400 space-y-3">
            <p>Bạn chưa tham gia lớp học nào.</p>
            <button
              onClick={() => setShowJoinModal(true)}
              className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 dark:text-indigo-400 rounded-xl text-xs font-bold transition-all cursor-pointer"
            >
              Gia nhập lớp học ngay
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {classrooms.map((cls) => (
              <div
                key={cls.id}
                onClick={() => setActiveClassroom(cls)}
                className="group p-5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-white dark:bg-zinc-900 hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-sm transition-all duration-200 cursor-pointer text-left"
              >
                <h3 className="text-sm font-bold text-zinc-800 dark:text-zinc-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {cls.class_name}
                </h3>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xs font-mono text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md">
                    {cls.class_code}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. Nhiệm vụ hàng ngày & Trợ lý AI */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between transition-all">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-zinc-200 dark:border-zinc-800 mb-6">
              <h2 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-zinc-50">
                Nhiệm vụ học tập hôm nay
              </h2>
              <span className="text-xs font-mono font-bold text-zinc-400 bg-zinc-50 dark:bg-zinc-950 px-2.5 py-1 rounded-lg border border-zinc-200 dark:border-zinc-800">
                {todayStrFormatted}
              </span>
            </div>

            {tasksLoading ? (
              <div className="py-12 text-center text-xs font-mono text-zinc-400 tracking-wider">
                Đang tải dữ liệu nhiệm vụ...
              </div>
            ) : tasks.length === 0 ? (
              <div className="py-12 text-center text-sm text-zinc-500 dark:text-zinc-400 tracking-wide space-y-4">
                <p>Hôm nay bạn không có lịch học hay nhiệm vụ nào.</p>
                <Link
                  href={ROUTES.STUDENT_GOALS}
                  className="inline-block px-5 py-2.5 bg-zinc-50 hover:bg-zinc-100 dark:bg-zinc-950 dark:hover:bg-zinc-900 border border-zinc-300 dark:border-zinc-700 hover:border-zinc-950 dark:hover:border-zinc-100 text-zinc-650 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-white rounded-xl font-bold text-xs"
                >
                  Tạo lộ trình ngay
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((task) => {
                  const isDone = task.status === "done";
                  return (
                    <div
                      key={task.id}
                      onClick={() => setActiveTask(task)}
                      className={`flex items-center justify-between p-4 border rounded-xl transition-all cursor-pointer ${
                        isDone
                          ? "border-zinc-100 dark:border-zinc-850 bg-zinc-50/50 dark:bg-zinc-950/20 opacity-60"
                          : "border-zinc-200 dark:border-zinc-800 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-zinc-900 hover:shadow-sm"
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all select-none ${
                            isDone
                              ? "bg-indigo-600 border-indigo-600 text-white"
                              : "border-zinc-300 dark:border-zinc-750 bg-white dark:bg-zinc-900"
                          }`}
                        >
                          {isDone && (
                            <span className="text-[10px] font-black">✓</span>
                          )}
                        </div>
                        <div>
                          <p
                            className={`text-sm font-bold text-zinc-800 dark:text-zinc-200 ${isDone ? "line-through text-zinc-400 dark:text-zinc-500" : ""}`}
                          >
                            {task.title}
                          </p>
                          <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
                            Lịch học: {task.start_time.substring(0, 5)} -{" "}
                            {task.end_time.substring(0, 5)}
                          </p>
                        </div>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-3 py-1 border rounded-full ${
                          isDone
                            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                            : task.status === "doing"
                              ? "bg-indigo-50/10 border-indigo-50/20 text-indigo-600 dark:text-indigo-400 animate-pulse"
                              : "bg-zinc-50 dark:bg-zinc-950 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500"
                        }`}
                      >
                        {isDone
                          ? "Đã xong"
                          : task.status === "doing"
                            ? "Đang làm"
                            : "Chưa làm"}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800 mt-6 flex justify-end">
            <Link
              href={ROUTES.STUDENT_GOALS}
              className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline tracking-wide"
            >
              Xem toàn bộ kế hoạch lộ trình học
            </Link>
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-900 via-indigo-950 to-zinc-950 dark:from-zinc-900 dark:to-zinc-950 text-zinc-50 p-8 rounded-2xl flex flex-col justify-between border border-zinc-200/5 dark:border-zinc-800 shadow-md">
          <div className="space-y-6">
            <div className="space-y-2">
              <span className="text-[10px] font-bold tracking-wider text-indigo-300 block uppercase">
                Gia sư AI 24/7
              </span>
              <h3 className="text-lg font-black tracking-tight">
                Trợ lý học tập thông minh
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed font-medium">
                Thảo luận trực tiếp cùng trợ lý học tập AI để được giải nghĩa lý thuyết, vẽ sơ đồ tư duy hoặc giải bài tập khó ngay lập tức.
              </p>
            </div>

            {!statsLoading &&
              stats?.weak_areas &&
              stats.weak_areas.length > 0 && (
                <div className="space-y-3 pt-5 border-t border-white/10 dark:border-zinc-800">
                  <span className="text-[10px] font-bold text-zinc-400 tracking-wider block uppercase">
                    Kiến thức cần củng cố
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {stats.weak_areas.map((topic: string) => (
                      <span
                        key={topic}
                        className="text-[9px] font-bold px-2.5 py-1 bg-white/10 dark:bg-zinc-800/80 border border-white/5 dark:border-zinc-700 text-indigo-200 dark:text-indigo-400 rounded-lg"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}
          </div>

          <Link
            href={ROUTES.STUDENT_CHAT}
            className="mt-8 px-5 py-3.5 bg-white hover:bg-zinc-100 text-indigo-950 rounded-xl font-bold text-xs text-center tracking-wider transition-all shadow-lg active:scale-[0.98] cursor-pointer"
          >
            Hỏi Gia sư AI ngay
          </Link>
        </div>
      </div>

      {/* Classroom join modal */}
      <ClassroomJoinModal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
        onSuccess={fetchClassrooms}
      />

      {/* Classroom detail modal */}
      <ClassroomDetailModal
        classroom={activeClassroom}
        onClose={() => setActiveClassroom(null)}
      />

      {/* Task study workspace modal */}
      <AnimatePresence>
        {activeTask && (
          <TaskStudyModal
            task={activeTask}
            onClose={() => setActiveTask(null)}
            onToggleStatus={handleToggleTaskStatus}
            onRefresh={fetchTodayTasks}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
