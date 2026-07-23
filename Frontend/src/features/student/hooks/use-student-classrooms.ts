"use client";

import { useCallback, useEffect, useState } from "react";
import { classroomService } from "@/features/student/services/classroom";
import type { Classroom } from "@/features/student/types";

export function useStudentClassrooms() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [classroomsLoading, setClassroomsLoading] = useState(true);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [activeClassroom, setActiveClassroom] = useState<Classroom | null>(null);

  const fetchClassrooms = useCallback(async () => {
    try {
      const response = await classroomService.listMine();
      setClassrooms(response.data);
    } catch (err) {
      console.error("Lỗi tải danh sách lớp học:", err);
    } finally {
      setClassroomsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClassrooms();
  }, [fetchClassrooms]);

  return {
    classrooms,
    classroomsLoading,
    showJoinModal,
    setShowJoinModal,
    activeClassroom,
    setActiveClassroom,
    fetchClassrooms,
  };
}
