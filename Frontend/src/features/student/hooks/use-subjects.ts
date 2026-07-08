"use client";

import { useCallback, useEffect, useState } from "react";
import { subjectService } from "@/features/student/services/subject";
import type { Subject } from "@/features/student/types";

interface UseSubjectsOptions {
  initialSubjects?: Subject[];
  fetchOnMount?: boolean;
}

export function useSubjects({
  initialSubjects = [],
  fetchOnMount = false,
}: UseSubjectsOptions = {}) {
  const [subjects, setSubjects] = useState<Subject[]>(initialSubjects);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubjects = useCallback(async (): Promise<Subject[]> => {
    setLoading(true);
    setError(null);
    try {
      const res = await subjectService.list();
      setSubjects(res.data);
      return res.data;
    } catch (err) {
      console.error("Lỗi tải danh sách môn học:", err);
      setError("Không thể tải danh sách môn học.");
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (fetchOnMount) {
      fetchSubjects();
    }
  }, [fetchOnMount, fetchSubjects]);

  return {
    subjects,
    setSubjects,
    loading,
    error,
    fetchSubjects,
  };
}
