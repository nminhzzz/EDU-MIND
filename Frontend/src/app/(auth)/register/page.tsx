"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import { toast } from "sonner";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User as UserIcon,
  Loader2,
  ArrowRight,
  GraduationCap,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { StudentGrade, UserRole } from "@/types/user";
import { parseApiError } from "@/utils/api-error";

export default function RegisterPage() {
  const { register, isLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [grade, setGrade] = useState<StudentGrade>("grade_10");

  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || !fullName) {
      toast.error("Vui lòng điền đầy đủ các thông tin bắt buộc.");
      return;
    }
    if (password.length < 8) {
      toast.error("Mật khẩu phải có ít nhất 8 ký tự.");
      return;
    }

    try {
      const payload = {
        email,
        password,
        full_name: fullName,
        role,
        grade: role === "student" ? grade : null,
      };
      await register(payload);
      toast.success("Đăng ký tài khoản thành công! Vui lòng đăng nhập.");
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Đăng ký thất bại. Vui lòng thử lại."));
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-6 bg-background">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/">
            <motion.div
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary text-primary-foreground font-black text-2xl shadow-sm mb-5 logo-em"
            >
              EM
            </motion.div>
          </Link>
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15, duration: 0.4 }}
            className="text-2xl md:text-3xl font-bold tracking-tight text-foreground text-balance"
          >
            Tạo tài khoản mới
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.25, duration: 0.4 }}
            className="text-muted-foreground mt-2 text-sm"
          >
            Đồng hành cùng AI trên lộ trình chinh phục tri thức
          </motion.p>
        </div>

        {/* Card Form */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.4 }}
          className="bg-card border border-border rounded-2xl p-6 sm:p-8 shadow-sm"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Vai trò Selection Tabs */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground block">
                Bạn là:
              </label>
              <div className="grid grid-cols-2 gap-1.5 p-1 bg-muted rounded-lg relative">
                <button
                  type="button"
                  onClick={() => setRole("student")}
                  className={`relative py-2 text-sm font-medium rounded-md transition-all cursor-pointer z-10 ${
                    role === "student"
                      ? "text-foreground bg-card shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Học sinh
                </button>
                <button
                  type="button"
                  onClick={() => setRole("teacher")}
                  className={`relative py-2 text-sm font-medium rounded-md transition-all cursor-pointer z-10 ${
                    role === "teacher"
                      ? "text-foreground bg-card shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  Giáo viên
                </button>
              </div>
            </div>

            {/* Full Name Input */}
            <div className="space-y-1.5">
              <label
                className="text-sm font-medium text-foreground block"
                htmlFor="fullName"
              >
                Họ và Tên
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-muted-foreground pointer-events-none">
                  <UserIcon className="h-5 w-5" />
                </span>
                <input
                  id="fullName"
                  type="text"
                  required
                  placeholder="Nguyễn Văn A"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-input rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring focus:ring-2 focus:ring-ring/25 transition-shadow disabled:opacity-50"
                />
              </div>
            </div>

            {/* Email Input */}
            <div className="space-y-1.5">
              <label
                className="text-sm font-medium text-foreground block"
                htmlFor="email"
              >
                Địa chỉ Email
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-muted-foreground pointer-events-none">
                  <Mail className="h-5 w-5" />
                </span>
                <input
                  id="email"
                  type="email"
                  required
                  placeholder="tenban@viethoc.edu.vn"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2.5 bg-background border border-input rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring focus:ring-2 focus:ring-ring/25 transition-shadow disabled:opacity-50"
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-1.5">
              <label
                className="text-sm font-medium text-foreground block"
                htmlFor="password"
              >
                Mật khẩu (tối thiểu 8 ký tự)
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-muted-foreground pointer-events-none">
                  <Lock className="h-5 w-5" />
                </span>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={8}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="w-full pl-10 pr-10 py-2.5 bg-background border border-input rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring focus:ring-2 focus:ring-ring/25 transition-shadow disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Dynamic Grade Selection (Only for Student role) */}
            <AnimatePresence>
              {role === "student" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-1.5 overflow-hidden"
                >
                  <label
                    className="text-sm font-medium text-foreground block"
                    htmlFor="grade"
                  >
                    Khối lớp học
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-muted-foreground pointer-events-none">
                      <GraduationCap className="h-5 w-5" />
                    </span>
                    <select
                      id="grade"
                      value={grade}
                      onChange={(e) => setGrade(e.target.value as StudentGrade)}
                      disabled={isLoading}
                      className="w-full pl-10 pr-4 py-2.5 bg-background border border-input rounded-lg text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-ring focus:ring-2 focus:ring-ring/25 transition-shadow disabled:opacity-50 appearance-none"
                    >
                      <optgroup label="Cấp 2 (Trung học cơ sở)">
                        <option value="grade_6">Khối lớp 6</option>
                        <option value="grade_7">Khối lớp 7</option>
                        <option value="grade_8">Khối lớp 8</option>
                        <option value="grade_9">Khối lớp 9</option>
                      </optgroup>
                      <optgroup label="Cấp 3 (Trung học phổ thông)">
                        <option value="grade_10">Khối lớp 10</option>
                        <option value="grade_11">Khối lớp 11</option>
                        <option value="grade_12">Khối lớp 12</option>
                      </optgroup>
                      <optgroup label="Đại học">
                        <option value="uni_year_1">Đại học năm 1</option>
                        <option value="uni_year_2">Đại học năm 2</option>
                        <option value="uni_year_3">Đại học năm 3</option>
                        <option value="uni_year_4">Đại học năm 4</option>
                      </optgroup>
                    </select>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg text-sm font-semibold shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70 active:scale-[0.99]"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Tạo tài khoản
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Footer Links */}
          <div className="text-center mt-6 pt-6 border-t border-border">
            <p className="text-sm text-muted-foreground">
              Đã có tài khoản?{" "}
              <Link
                href={ROUTES.LOGIN}
                className="font-semibold text-primary hover:underline"
              >
                Đăng nhập ngay
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
