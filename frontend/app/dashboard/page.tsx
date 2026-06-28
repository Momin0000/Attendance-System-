"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import StatCard from "@/components/cards/StatCard";
import { analyticsApi } from "@/lib/api";
import { DashboardStats } from "@/types";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Legend,
} from "recharts";
import { Users, Building2, BookOpen, GraduationCap, TrendingUp, AlertTriangle } from "lucide-react";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.dashboard()
      .then((res) => setStats(res.data))
      .catch(() => toast.error("Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <AppLayout>
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </AppLayout>
  );

  return (
    <AppLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Bano Qabil Pakistan — Attendance Overview</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
        <StatCard title="Total Students" value={stats?.total_students ?? 0} icon={GraduationCap} color="text-blue-600" />
        <StatCard title="Active Students" value={stats?.active_students ?? 0} icon={Users} color="text-green-600" />
        <StatCard title="Campuses" value={stats?.total_campuses ?? 0} icon={Building2} color="text-purple-600" />
        <StatCard title="Batches" value={stats?.total_batches ?? 0} icon={BookOpen} color="text-orange-600" />
        <StatCard
          title="Today's Attendance"
          value={`${stats?.today_attendance_percentage ?? 0}%`}
          icon={TrendingUp}
          color={stats && stats.today_attendance_percentage >= 75 ? "text-green-600" : "text-red-600"}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Weekly Trend */}
        <div className="card">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Weekly Attendance Trend</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={stats?.weekly_attendance_trend ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
              <Tooltip formatter={(v: number) => `${v}%`} />
              <Line type="monotone" dataKey="percentage" stroke="#1e3a5f" strokeWidth={2} dot={{ r: 3 }} name="Attendance %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Campus-wise Bar */}
        <div className="card">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Campus-wise Students</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={stats?.campus_wise_stats ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="campus_name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_students" fill="#1e3a5f" name="Total" radius={[4,4,0,0]} />
              <Bar dataKey="active_students" fill="#3b82f6" name="Active" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Campus Table */}
      <div className="card">
        <h2 className="text-base font-semibold text-gray-800 mb-4">Campus Performance</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="table-th">Campus</th>
                <th className="table-th">Students</th>
                <th className="table-th">Batches</th>
                <th className="table-th">Avg Attendance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {stats?.campus_wise_stats.map((c) => (
                <tr key={c.campus_id} className="hover:bg-gray-50">
                  <td className="table-td font-medium">{c.campus_name}</td>
                  <td className="table-td">{c.total_students}</td>
                  <td className="table-td">{c.total_batches}</td>
                  <td className="table-td">
                    <span className={`font-semibold ${c.avg_attendance_percentage >= 75 ? "text-green-600" : "text-red-600"}`}>
                      {c.avg_attendance_percentage}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
}
