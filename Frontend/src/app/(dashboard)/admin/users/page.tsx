"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import Link from "next/link";

import { UserFilterBar } from "@/components/admin/user-filter-bar";
import { UserTable } from "@/components/admin/user-table";
import { UserModal } from "@/components/admin/user-modal";

interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  grade: string | null;
}

export default function AdminUsersPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Bộ lọc states
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<AdminUser | null>(null);
  const [formLoading, setFormLoading] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (roleFilter) params.role = roleFilter;
      if (statusFilter) params.is_active = statusFilter === "active";
      
      const res = await apiClient.get<AdminUser[]>("/users/admin/users", { params });
      setUsers(res.data);
    } catch (err: any) {
      console.error("Lỗi tải danh sách người dùng:", err);
      setError("Không thể kết nối đến máy chủ.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push("/login");
        return;
      }
      if (user?.role !== "admin") {
        setError("Bạn không có quyền truy cập trang quản trị này.");
        setLoading(false);
        return;
      }
      fetchUsers();
    }
  }, [isLoading, isAuthenticated, user, router, roleFilter, statusFilter]);

  const handleOpenAddModal = () => {
    setEditingUser(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (u: AdminUser) => {
    setEditingUser(u);
    setIsModalOpen(true);
  };

  const handleSubmitForm = async (payload: any) => {
    setFormLoading(true);
    try {
      if (editingUser) {
        await apiClient.patch(`/users/admin/users/${editingUser.id}`, payload);
        toast.success("Cập nhật tài khoản thành viên thành công!");
      } else {
        await apiClient.post("/users/admin/users", payload);
        toast.success("Tạo tài khoản thành viên mới thành công!");
      }
      setIsModalOpen(false);
      fetchUsers();
    } catch (err: any) {
      const msg = err.response?.data?.detail;
      toast.error(typeof msg === "string" ? msg : "Thao tác thất bại.");
    } finally {
      setFormLoading(false);
    }
  };

  const handleToggleStatus = async (u: AdminUser) => {
    try {
      await apiClient.patch(`/users/admin/users/${u.id}`, {
        is_active: !u.is_active
      });
      toast.success(`Đã cập nhật trạng thái hoạt động của tài khoản.`);
      fetchUsers();
    } catch (err: any) {
      const msg = err.response?.data?.detail;
      toast.error(typeof msg === "string" ? msg : "Không thể thay đổi trạng thái hoạt động.");
    }
  };

  const handleDeleteUser = async (u: AdminUser) => {
    if (!confirm(`Bạn có chắc chắn muốn xóa tài khoản ${u.email} khỏi hệ thống?`)) return;
    
    try {
      await apiClient.delete(`/users/admin/users/${u.id}`);
      toast.success("Đã xóa tài khoản khỏi cơ sở dữ liệu.");
      fetchUsers();
    } catch (err) {
      toast.error("Xóa tài khoản thất bại.");
    }
  };

  const filteredUsers = users.filter(u => {
    const query = searchQuery.toLowerCase().trim();
    if (!query) return true;
    return (
      u.email.toLowerCase().includes(query) ||
      (u.full_name && u.full_name.toLowerCase().includes(query))
    );
  });

  if (isLoading || loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
          Đang tải danh sách thành viên...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto text-center py-20 space-y-6">
        <div className="w-16 h-16 bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20 rounded-full flex items-center justify-center text-2xl font-black mx-auto">
          !
        </div>
        <div className="space-y-2">
          <h2 className="text-lg font-black text-zinc-950 dark:text-white uppercase">
            TRUY CẬP BỊ TỪ CHỐI
          </h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
            {error}
          </p>
        </div>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs"
        >
          Quay lại Trang chủ
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-left">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-sans font-bold tracking-wider text-indigo-600 dark:text-indigo-400 block uppercase">
            Phân hệ Quản lý
          </span>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white tracking-tight">
            QUẢN LÝ THÀNH VIÊN
          </h1>
        </div>
        
        <button
          onClick={handleOpenAddModal}
          className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs tracking-wider transition-all shadow-lg shadow-indigo-500/15 cursor-pointer flex items-center justify-center"
        >
          Thêm thành viên mới +
        </button>
      </div>

      <UserFilterBar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        roleFilter={roleFilter}
        setRoleFilter={setRoleFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
      />

      <UserTable
        users={filteredUsers}
        onToggleStatus={handleToggleStatus}
        onEdit={handleOpenEditModal}
        onDelete={handleDeleteUser}
      />

      <UserModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        editingUser={editingUser}
        onSubmit={handleSubmitForm}
        formLoading={formLoading}
      />
    </div>
  );
}
