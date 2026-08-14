import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function DashboardNotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <span className="text-sm font-bold text-indigo-600">404</span>
      <h1 className="mt-2 text-2xl font-bold text-zinc-950 dark:text-white">Không tìm thấy nội dung</h1>
      <p className="mt-2 max-w-md text-sm text-zinc-500 dark:text-zinc-400">Trang có thể đã được di chuyển hoặc bạn không còn quyền truy cập.</p>
      <Link href="/" className="mt-6 inline-flex h-10 items-center gap-2 rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white hover:bg-indigo-700">
        <ArrowLeft className="size-4" /> Quay về trang chủ
      </Link>
    </div>
  );
}
