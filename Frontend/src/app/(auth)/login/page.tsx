"use client";

import React, { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";
import { Eye, EyeOff, Lock, Mail, Loader2, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

function LoginForm() {
  const { login, isLoading } = useAuth();
  const searchParams = useSearchParams();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Vui lòng điền đầy đủ email và mật khẩu.");
      return;
    }

    try {
      const redirectTo = searchParams.get("redirect") ?? undefined;
      await login(email, password, redirectTo);
      toast.success("Đăng nhập thành công!");
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Đăng nhập thất bại. Vui lòng kiểm tra lại."));
    }

  };

  return (
    <div className="w-full max-w-md">
      {/* Logo / Header */}
      <div className="text-center mb-8">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white font-black text-2xl shadow-lg shadow-indigo-500/20 mb-4 logo-em"
        >
          EM
        </motion.div>
        <motion.h1 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-zinc-900 via-zinc-800 to-zinc-900 dark:from-white dark:via-zinc-200 dark:to-white bg-clip-text text-transparent"
        >
          Chào mừng quay lại
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-zinc-500 dark:text-zinc-400 mt-2 text-sm"
        >
          Học tập thông minh hơn với sự hỗ trợ của trí tuệ nhân tạo
        </motion.p>
      </div>

      {/* Card Form */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl dark:shadow-zinc-950/50"
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Input */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 block" htmlFor="email">
              Địa chỉ Email
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-zinc-400 pointer-events-none">
                <Mail className="h-5 w-5" />
              </span>
              <input
                id="email"
                type="email"
                required
                autoFocus
                placeholder="tenban@viethoc.edu.vn"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="w-full pl-11 pr-4 py-3 bg-zinc-50 dark:bg-zinc-950/50 rounded-2xl text-sm text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>
          </div>

          {/* Password Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 block" htmlFor="password">
                Mật khẩu
              </label>
              <Link 
                href="/forgot-password" 
                className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Quên mật khẩu?
              </Link>
            </div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-zinc-400 pointer-events-none">
                <Lock className="h-5 w-5" />
              </span>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="w-full pl-11 pr-11 py-3 bg-zinc-50 dark:bg-zinc-950/50 rounded-2xl text-sm text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200"
              >
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="relative w-full py-3.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-2xl text-sm font-semibold shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-75 disabled:cursor-not-allowed overflow-hidden active:scale-[0.98]"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                Đăng nhập
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        {/* Footer Links */}
        <div className="text-center mt-6 pt-6">
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Chưa có tài khoản?{" "}
            <Link 
              href={ROUTES.REGISTER} 
              className="font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Đăng ký ngay
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-6 bg-gradient-to-tr from-zinc-50 via-zinc-100 to-indigo-50/30 dark:from-zinc-950 dark:via-zinc-900 dark:to-zinc-950 relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-500/5 blur-[120px] pointer-events-none" />

      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      }>
        <LoginForm />
      </Suspense>
    </div>
  );
}
