"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, UserPlus, X } from "lucide-react";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";

interface AddStudentModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (email: string) => Promise<void>;
}

export function AddStudentModal({
  open,
  onClose,
  onSubmit,
}: AddStudentModalProps) {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error("Vui lòng nhập email học sinh.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit(email.trim());
      setEmail("");
      onClose();
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Không thể thêm học sinh."));
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (submitting) return;
    setEmail("");
    onClose();
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black z-40"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-md p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-black text-zinc-900 dark:text-white">
                  Thêm học sinh vào lớp
                </h2>
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={submitting}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-600 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer disabled:opacity-50"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-1.5">
                    Email học sinh *
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student@example.com"
                    disabled={submitting}
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none disabled:opacity-60"
                  />
                </div>
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
                >
                  {submitting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <UserPlus className="w-4 h-4" />
                  )}
                  {submitting ? "Đang thêm..." : "Thêm học sinh"}
                </button>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
