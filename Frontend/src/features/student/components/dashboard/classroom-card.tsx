"use client";

import React from "react";
import type { Classroom } from "@/features/student/types";

interface ClassroomCardProps {
  classroom: Classroom;
  onClick: (classroom: Classroom) => void;
}

export function ClassroomCard({ classroom, onClick }: ClassroomCardProps) {
  return (
    <div
      onClick={() => onClick(classroom)}
      className="group p-5 border border-border rounded-xl bg-card hover:border-ring/50 hover:shadow-sm transition-all duration-200 cursor-pointer text-left"
    >
      <h3 className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
        {classroom.class_name}
      </h3>
      <div className="flex items-center gap-3 mt-2">
        <span className="text-xs font-mono text-primary bg-primary/10 px-2 py-0.5 rounded-md">
          {classroom.class_code}
        </span>
      </div>
    </div>
  );
}
