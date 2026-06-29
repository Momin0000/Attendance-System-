"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/utils";
import {
  LayoutDashboard, Users, ScanLine,
  FileDown, Settings, LogOut, GraduationCap, Menu, X,
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
  const [open, setOpen] = useState(false);
  const isAdmin = user?.role === "super_admin" || user?.role === "campus_admin";

  const NavContent = () => (
    <>
      <div className="p-4 border-b border-primary-500">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center p-1">
            <img src="/logo.png" alt="BQ" className="w-full h-full object-contain" />
          </div>
          <div>
            <p className="text-white font-bold text-sm leading-tight">Bano Qabil</p>
            <p className="text-primary-200 text-xs">Attendance System</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href} onClick={() => setOpen(false)}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
              pathname.startsWith(href)
                ? "bg-white text-primary-700"
                : "text-primary-100 hover:bg-primary-500 hover:text-white"
            )}>
            <Icon className="w-4 h-4 flex-shrink-0" />{label}
          </Link>
        ))}
        {isAdmin && (
          <>
            <div className="pt-3 pb-1">
              <p className="text-primary-300 text-xs font-semibold uppercase tracking-wider px-3">Admin</p>
            </div>
            {adminItems.map(({ href, label, icon: Icon }) => (
              <Link key={href} href={href} onClick={() => setOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  pathname.startsWith(href)
                    ? "bg-white text-primary-700"
                    : "text-primary-100 hover:bg-primary-500 hover:text-white"
                )}>
                <Icon className="w-4 h-4 flex-shrink-0" />{label}
              </Link>
            ))}
          </>
        )}
      </nav>
      <div className="p-4 border-t border-primary-500">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-primary-400 flex items-center justify-center">
            <span className="text-white text-xs font-semibold">{user?.full_name?.charAt(0).toUpperCase()}</span>
          </div>
          <div className="min-w-0">
            <p className="text-white text-xs font-medium truncate">{user?.full_name}</p>
            <p className="text-primary-300 text-xs capitalize">{user?.role?.replace("_", " ")}</p>
          </div>
        </div>
        <button onClick={() => { logout(); window.location.href = "/auth"; }}
          className="flex items-center gap-2 text-primary-200 hover:text-white text-xs w-full px-2 py-1.5 rounded hover:bg-primary-500 transition-colors">
          <LogOut className="w-3.5 h-3.5" /> Sign Out
        </button>
      </div>
    </>
  );

  return (
    <>
      <div className="lg:hidden fixed top-0 left-0 right-0 z-40 bg-primary-600 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-white rounded-lg flex items-center justify-center p-0.5">
            <img src="/logo.png" alt="BQ" className="w-full h-full object-contain" />
          </div>
          <span className="text-white font-bold text-sm">Bano Qabil</span>
        </div>
        <button onClick={() => setOpen(!open)} className="text-white p-1">
          {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>
      {open && (
        <div className="lg:hidden fixed inset-0 z-30 bg-black/50" onClick={() => setOpen(false)} />
      )}
      <aside className={`lg:hidden fixed top-0 left-0 h-full w-64 bg-primary-600 z-40 flex flex-col transform transition-transform duration-300 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <NavContent />
      </aside>
      <aside className="hidden lg:flex w-64 min-h-screen bg-primary-600 flex-col">
        <NavContent />
      </aside>
    </>
  );
}
