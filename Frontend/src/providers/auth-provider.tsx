"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { User, AuthState } from "@/types/user";
import { userApi } from "@/services/user";
import { ROUTES } from "@/constants/routes";

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const router = useRouter();

  // Khôi phục phiên đăng nhập từ cookie access_token (nếu có)
  const checkAuth = async () => {
    try {
      const response = await userApi.getMe();
      setState({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (_) {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Đăng nhập
  const login = async (email: string, password: string) => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }));
    try {
      await userApi.login(email, password);
      
      // Lấy thông tin user vừa đăng nhập thành công
      const userResponse = await userApi.getMe();
      const user = userResponse.data;

      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });

      // Chuyển hướng theo vai trò (Role)
      if (user.role === "admin") {
        router.push(ROUTES.ADMIN);
      } else if (user.role === "teacher") {
        router.push(ROUTES.TEACHER_DASHBOARD);
      } else {
        router.push(ROUTES.STUDENT_DASHBOARD);
      }
    } catch (error) {
      setState((prev: AuthState) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  // Đăng ký tài khoản mới
  const register = async (data: any) => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }));
    try {
      await userApi.register(data);
      setState((prev: AuthState) => ({ ...prev, isLoading: false }));
      router.push(ROUTES.LOGIN);
    } catch (error) {
      setState((prev: AuthState) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  // Đăng xuất
  const logout = async () => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }));
    try {
      await userApi.logout();
    } catch (e) {
      console.warn("Lỗi khi đăng xuất trên server:", e);
    } finally {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
      router.push(ROUTES.LOGIN);
    }
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
}
