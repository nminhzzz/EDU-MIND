"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { User, AuthState, RegisterRequest } from "@/types/user";
import { userApi } from "@/services/user";
import { ROUTES } from "@/constants/routes";
import { getSafeRedirectPath } from "@/lib/safe-redirect";

interface AuthContextType extends AuthState {
  login: (email: string, password: string, redirectTo?: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function getDefaultDashboard(role: User["role"]): string {
  if (role === "admin") return ROUTES.ADMIN;
  if (role === "teacher") return ROUTES.TEACHER_DASHBOARD;
  return ROUTES.STUDENT_DASHBOARD;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const router = useRouter();

  const checkAuth = async () => {
    const AUTH_TIMEOUT_MS = 12_000;

    try {
      const response = await Promise.race([
        userApi.getMe(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error("Auth timeout")), AUTH_TIMEOUT_MS),
        ),
      ]);
      setState({
        user: response.data,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
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

  const login = async (email: string, password: string, redirectTo?: string) => {
    setState((prev: AuthState) => ({ ...prev, isLoading: true }));
    try {
      await userApi.login(email, password);

      const userResponse = await userApi.getMe();
      const user = userResponse.data;

      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });

      const destination =
        getSafeRedirectPath(redirectTo, user.role) ?? getDefaultDashboard(user.role);
      router.push(destination);
    } catch (error) {
      setState((prev: AuthState) => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  const register = async (data: RegisterRequest) => {
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
