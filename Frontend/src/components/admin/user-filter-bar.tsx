"use client";

import React from "react";
import Link from "next/link";

interface UserFilterBarProps {
  searchQuery: string;
  setSearchQuery: (val: string) => void;
  roleFilter: string;
  setRoleFilter: (val: string) => void;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
}

export function UserFilterBar({
  searchQuery,
  setSearchQuery,
  roleFilter,
  setRoleFilter,
  statusFilter,
  setStatusFilter,
}: UserFilterBarProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl">
      <input
        type="text"
        placeholder="Tìm email hoặc họ tên..."
        value={searchQuery}
        onChange={e => setSearchQuery(e.target.value)}
        className="w-full px-4 py-2.5 text-xs border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white font-medium"
      />

      <select
        value={roleFilter}
        onChange={e => setRoleFilter(e.target.value)}
        className="px-4 py-2.5 text-xs border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white font-bold cursor-pointer"
      >
        <option value="">Tất cả vai trò</option>
        <option value="student">Học sinh</option>
        <option value="teacher">Giáo viên</option>
        <option value="admin">Quản trị viên</option>
      </select>

      <select
        value={statusFilter}
        onChange={e => setStatusFilter(e.target.value)}
        className="px-4 py-2.5 text-xs border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white font-bold cursor-pointer"
      >
        <option value="">Tất cả trạng thái</option>
        <option value="active">Hoạt động</option>
        <option value="blocked">Đang khóa</option>
      </select>

      <Link
        href="/admin"
        className="px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 hover:border-zinc-900 dark:hover:border-zinc-100 text-zinc-650 dark:text-zinc-350 hover:text-zinc-900 dark:hover:text-white text-xs font-bold rounded-xl flex items-center justify-center"
      >
        Quay lại Dashboard &rarr;
      </Link>

    </div>
  );
}
