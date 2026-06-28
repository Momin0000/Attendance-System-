"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { userApi, campusApi } from "@/lib/api";
import { Campus } from "@/types";
import toast from "react-hot-toast";
import { Plus, Pencil, Trash2, KeyRound } from "lucide-react";
import { useForm } from "react-hook-form";
import { formatDate } from "@/utils";

interface UserRow {
  id: number;
  email: string;
  full_name: string;
  role: string;
  campus_id: number | null;
  is_active: boolean;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editUser, setEditUser] = useState<UserRow | null>(null);
  const [showResetModal, setShowResetModal] = useState<UserRow | null>(null);
  const [newPassword, setNewPassword] = useState("");

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm();

  const fetchUsers = async () => {
    try {
      const res = await userApi.list();
      setUsers(res.data.users || res.data);
    } catch { toast.error("Failed to load users"); }
  };

  useEffect(() => {
    fetchUsers();
    campusApi.list().then((r) => setCampuses(r.data));
  }, []);

  const openCreate = () => { setEditUser(null); reset({}); setShowForm(true); };
  const openEdit = (u: UserRow) => { setEditUser(u); reset({ ...u, password: "" }); setShowForm(true); };

  const onSubmit = async (data: any) => {
    try {
      const payload = { ...data, campus_id: data.campus_id ? Number(data.campus_id) : null };
      if (editUser) {
        delete payload.password;
        await userApi.update(editUser.id, payload);
        toast.success("User updated");
      } else {
        await userApi.create(payload);
        toast.success("User created");
      }
      setShowForm(false); fetchUsers();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to save user");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this user? This cannot be undone.")) return;
    try {
      await userApi.delete(id);
      toast.success("User deleted"); fetchUsers();
    } catch { toast.error("Failed to delete"); }
  };

  const handleResetPassword = async () => {
    if (!newPassword || newPassword.length < 6) { toast.error("Password must be at least 6 characters"); return; }
    try {
      await userApi.resetPassword(showResetModal!.id, newPassword);
      toast.success("Password reset successfully");
      setShowResetModal(null); setNewPassword("");
    } catch { toast.error("Failed to reset password"); }
  };

  const roleColors: Record<string, string> = {
    super_admin: "bg-purple-100 text-purple-800",
    campus_admin: "bg-blue-100 text-blue-800",
    teacher: "bg-green-100 text-green-800",
    attendance_operator: "bg-yellow-100 text-yellow-800",
    student: "bg-gray-100 text-gray-800",
  };

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-500 text-sm mt-1">{users.length} total users</p>
        </div>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add User
        </button>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="table-th">Name</th><th className="table-th">Email</th>
                <th className="table-th">Role</th><th className="table-th">Campus</th>
                <th className="table-th">Status</th><th className="table-th">Created</th>
                <th className="table-th">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="table-td font-medium">{u.full_name}</td>
                  <td className="table-td text-gray-500">{u.email}</td>
                  <td className="table-td">
                    <span className={`badge ${roleColors[u.role] || "bg-gray-100 text-gray-800"}`}>
                      {u.role.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="table-td text-gray-500">{campuses.find((c) => c.id === u.campus_id)?.name || "—"}</td>
                  <td className="table-td">
                    <span className={`badge ${u.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="table-td text-gray-500">{formatDate(u.created_at)}</td>
                  <td className="table-td">
                    <div className="flex gap-1">
                      <button onClick={() => openEdit(u)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500" title="Edit"><Pencil className="w-3.5 h-3.5" /></button>
                      <button onClick={() => { setShowResetModal(u); setNewPassword(""); }} className="p-1.5 hover:bg-yellow-50 rounded text-yellow-600" title="Reset Password"><KeyRound className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(u.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400" title="Delete"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-semibold mb-4">{editUser ? "Edit User" : "Create User"}</h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div><label className="label">Full Name *</label><input className="input" {...register("full_name", { required: true })} /></div>
              <div><label className="label">Email *</label><input type="email" className="input" {...register("email", { required: true })} /></div>
              {!editUser && <div><label className="label">Password *</label><input type="password" className="input" {...register("password", { required: !editUser })} /></div>}
              <div><label className="label">Role *</label>
                <select className="input" {...register("role", { required: true })}>
                  <option value="">Select Role</option>
                  <option value="super_admin">Super Admin</option>
                  <option value="campus_admin">Campus Admin</option>
                  <option value="teacher">Teacher</option>
                  <option value="attendance_operator">Attendance Operator</option>
                </select>
              </div>
              <div><label className="label">Campus</label>
                <select className="input" {...register("campus_id")}>
                  <option value="">All Campuses</option>
                  {campuses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn-primary">{isSubmitting ? "Saving..." : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reset Password Modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-semibold mb-2">Reset Password</h2>
            <p className="text-sm text-gray-500 mb-4">For: <strong>{showResetModal.full_name}</strong></p>
            <input type="password" className="input mb-4" placeholder="New password (min 6 chars)" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
            <div className="flex justify-end gap-3">
              <button onClick={() => setShowResetModal(null)} className="btn-secondary">Cancel</button>
              <button onClick={handleResetPassword} className="btn-primary">Reset Password</button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
