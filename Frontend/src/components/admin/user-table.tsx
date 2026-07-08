import React from "react";
import { AdminUser } from "@/types/admin";

interface UserTableProps {
  users: AdminUser[];
  onToggleStatus: (u: AdminUser) => void;
  onEdit: (u: AdminUser) => void;
  onDelete: (u: AdminUser) => void;
}

const roleLabels: Record<string, string> = {
  student: "Học sinh",
  teacher: "Giáo viên",
  admin: "Admin",
};

export function UserTable({ users, onToggleStatus, onEdit, onDelete }: UserTableProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="border-b border-zinc-250 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 text-zinc-500 uppercase font-extrabold tracking-wider">
              <th className="px-6 py-4">Tên & Email</th>
              <th className="px-6 py-4">Vai trò</th>
              <th className="px-6 py-4">Khối lớp</th>
              <th className="px-6 py-4">Trạng thái</th>
              <th className="px-6 py-4">Ngày tạo</th>
              <th className="px-6 py-4 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {users.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-zinc-400 font-mono">
                  Không tìm thấy thành viên nào phù hợp.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="hover:bg-zinc-50/40 dark:hover:bg-zinc-950/10 transition-colors font-medium">
                  <td className="px-6 py-4">
                    <div className="font-extrabold text-zinc-900 dark:text-white">
                      {u.full_name || "Chưa thiết lập tên"}
                    </div>
                    <div className="text-[10px] text-zinc-400 dark:text-zinc-500 font-mono font-medium mt-0.5">
                      {u.email}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2.5 py-0.5 border rounded-full text-[9px] font-bold ${
                        u.role === "admin"
                          ? "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400"
                          : u.role === "teacher"
                          ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-600 dark:text-indigo-400"
                          : "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                      }`}
                    >
                      {roleLabels[u.role] || u.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono">
                    {u.grade ? u.grade.replace("grade_", "Lớp ").replace("uni_year_", "Năm SV ") : "--"}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => onToggleStatus(u)}
                      className={`px-3 py-1 rounded-full border text-[10px] font-bold transition-all cursor-pointer ${
                        u.is_active
                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                          : "bg-zinc-50 dark:bg-zinc-950 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500"
                      }`}
                    >
                      {u.is_active ? "Hoạt động" : "Đã khóa"}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-zinc-400 dark:text-zinc-500 font-mono text-[10px]">
                    {new Date(u.created_at).toLocaleDateString("vi-VN")}
                  </td>
                  <td className="px-6 py-4 text-right space-x-3">
                    <button
                      onClick={() => onEdit(u)}
                      className="text-indigo-600 dark:text-indigo-450 hover:underline font-bold cursor-pointer"
                    >
                      Sửa
                    </button>
                    <button
                      onClick={() => onDelete(u)}
                      className="text-red-600 dark:text-red-450 hover:underline font-bold cursor-pointer"
                    >
                      Xóa
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
