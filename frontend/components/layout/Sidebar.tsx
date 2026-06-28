"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/utils";
import {
  LayoutDashboard, Users, BookOpen, ScanLine,
  BarChart2, FileDown, Settings, LogOut, GraduationCap,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/students", label: "Students", icon: GraduationCap },
  { href: "/attendance", label: "Attendance", icon: ScanLine },
  { href: "/reports", label: "Reports", icon: FileDown },
  { href: "/settings", label: "Settings", icon: Settings },
];

const adminItems = [
  { href: "/users", label: "Users", icon: Users },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const isAdmin = user?.role === "super_admin" || user?.role === "campus_admin";

  return (
    <aside className="w-64 min-h-screen bg-primary-600 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-primary-500">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center p-0.5"><img src="/logo.png" alt="BQ" className="w-full h-full object-contain" /></div>
          <div>
            <p className="text-white font-bold text-sm leading-tight">Bano Qabil</p>
            <p className="text-primary-200 text-xs">Attendance System</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
              pathname.startsWith(href)
                ? "bg-white text-primary-700"
                : "text-primary-100 hover:bg-primary-500 hover:text-white"
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </Link>
        ))}

        {isAdmin && (
          <>
            <div className="pt-4 pb-2">
              <p className="text-primary-300 text-xs font-semibold uppercase tracking-wider px-3">Admin</p>
            </div>
            {adminItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  pathname.startsWith(href)
                    ? "bg-white text-primary-700"
                    : "text-primary-100 hover:bg-primary-500 hover:text-white"
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {label}
              </Link>
            ))}
          </>
        )}
      </nav>

      {/* User footer */}
      <div className="p-4 border-t border-primary-500">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-primary-400 flex items-center justify-center">
            <span className="text-white text-xs font-semibold">
              {user?.full_name?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="min-w-0">
            <p className="text-white text-xs font-medium truncate">{user?.full_name}</p>
            <p className="text-primary-300 text-xs capitalize">{user?.role?.replace("_", " ")}</p>
          </div>
        </div>
        <button
          onClick={() => { logout(); window.location.href = "/auth"; }}
          className="flex items-center gap-2 text-primary-200 hover:text-white text-xs w-full px-2 py-1.5 rounded hover:bg-primary-500 transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" /> Sign Out
        </button>
      </div>
    </aside>
  );
}
