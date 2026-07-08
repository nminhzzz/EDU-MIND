"use client";

import React from "react";
import {
  AiTutorPromoCard,
  ClassroomDetailModal,
  ClassroomJoinModal,
  ClassroomSection,
  DashboardKpiRow,
  StudentWelcomeBanner,
  TodayTasksCard,
} from "@/features/student/components/dashboard";
import { useDashboard } from "@/features/student/hooks/use-dashboard";
import { useAuth } from "@/hooks/use-auth";

export default function StudentDashboard() {
  const { user } = useAuth();
  const {
    stats,
    statsLoading,
    tasks,
    tasksLoading,
    classrooms,
    classroomsLoading,
    showJoinModal,
    setShowJoinModal,
    activeClassroom,
    setActiveClassroom,
    fetchClassrooms,
  } = useDashboard();

  const todayStrFormatted = new Date().toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  return (
    <div className="space-y-6 text-left">
      <StudentWelcomeBanner
        fullName={user?.full_name || "Học sinh"}
        onJoinClassClick={() => setShowJoinModal(true)}
      />

      <DashboardKpiRow stats={stats} statsLoading={statsLoading} />

      <ClassroomSection
        classrooms={classrooms}
        loading={classroomsLoading}
        onJoinClick={() => setShowJoinModal(true)}
        onSelectClassroom={setActiveClassroom}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <TodayTasksCard
          tasks={tasks}
          loading={tasksLoading}
          todayLabel={todayStrFormatted}
        />
        <AiTutorPromoCard stats={stats} statsLoading={statsLoading} />
      </div>

      <ClassroomJoinModal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
        onSuccess={fetchClassrooms}
      />

      <ClassroomDetailModal
        classroom={activeClassroom}
        onClose={() => setActiveClassroom(null)}
      />
    </div>
  );
}
