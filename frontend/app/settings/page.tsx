"use client";
import { useEffect, useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { campusApi, courseApi, batchApi } from "@/lib/api";
import { Campus, Course, Batch } from "@/types";
import toast from "react-hot-toast";
import { Plus, Pencil, Trash2, Building2, BookOpen, Users } from "lucide-react";
import { useForm } from "react-hook-form";

type Tab = "campuses" | "courses" | "batches";

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>("campuses");
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editItem, setEditItem] = useState<any>(null);

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm();

  const fetch = async () => {
    try {
      const [c, co, b] = await Promise.all([campusApi.list(), courseApi.list(), batchApi.list()]);
      setCampuses(c.data); setCourses(co.data); setBatches(b.data);
    } catch { toast.error("Failed to load data"); }
  };
  useEffect(() => { fetch(); }, []);

  const openCreate = () => { setEditItem(null); reset({}); setShowForm(true); };
  const openEdit = (item: any) => { setEditItem(item); reset(item); setShowForm(true); };

  const onSubmit = async (data: any) => {
    try {
      if (tab === "campuses") {
        editItem ? await campusApi.update(editItem.id, data) : await campusApi.create(data);
      } else if (tab === "courses") {
        const payload = { ...data, campus_id: Number(data.campus_id), duration_months: Number(data.duration_months) };
        editItem ? await courseApi.update(editItem.id, payload) : await courseApi.create(payload);
      } else {
        const payload = { ...data, campus_id: Number(data.campus_id), course_id: Number(data.course_id) };
        editItem ? await batchApi.update(editItem.id, payload) : await batchApi.create(payload);
      }
      toast.success(editItem ? "Updated!" : "Created!");
      setShowForm(false); fetch();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to save");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this item?")) return;
    try {
      if (tab === "campuses") await campusApi.delete(id);
      else if (tab === "courses") await courseApi.delete(id);
      else await batchApi.delete(id);
      toast.success("Deleted"); fetch();
    } catch { toast.error("Failed to delete"); }
  };

  const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: "campuses", label: "Campuses", icon: Building2 },
    { key: "courses", label: "Courses", icon: BookOpen },
    { key: "batches", label: "Batches", icon: Users },
  ];

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <button onClick={openCreate} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add {tab.slice(0, -1).charAt(0).toUpperCase() + tab.slice(0, -1).slice(1)}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-xl w-fit">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button key={key} onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === key ? "bg-white shadow text-primary-700" : "text-gray-500 hover:text-gray-700"}`}>
            <Icon className="w-4 h-4" /> {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          {tab === "campuses" && (
            <table className="w-full">
              <thead className="bg-gray-50 border-b"><tr>
                <th className="table-th">Name</th><th className="table-th">Code</th>
                <th className="table-th">City</th><th className="table-th">Phone</th>
                <th className="table-th">Status</th><th className="table-th">Actions</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-100">
                {campuses.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="table-td font-medium">{c.name}</td>
                    <td className="table-td font-mono text-xs">{c.code}</td>
                    <td className="table-td">{c.city}</td>
                    <td className="table-td text-gray-500">{c.phone || "—"}</td>
                    <td className="table-td"><span className={`badge ${c.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>{c.is_active ? "Active" : "Inactive"}</span></td>
                    <td className="table-td"><div className="flex gap-1">
                      <button onClick={() => openEdit(c)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500"><Pencil className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(c.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {tab === "courses" && (
            <table className="w-full">
              <thead className="bg-gray-50 border-b"><tr>
                <th className="table-th">Name</th><th className="table-th">Code</th>
                <th className="table-th">Duration</th><th className="table-th">Campus</th>
                <th className="table-th">Actions</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-100">
                {courses.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="table-td font-medium">{c.name}</td>
                    <td className="table-td font-mono text-xs">{c.code}</td>
                    <td className="table-td">{c.duration_months ? `${c.duration_months} months` : "—"}</td>
                    <td className="table-td">{campuses.find((x) => x.id === c.campus_id)?.name || "—"}</td>
                    <td className="table-td"><div className="flex gap-1">
                      <button onClick={() => openEdit(c)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500"><Pencil className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(c.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {tab === "batches" && (
            <table className="w-full">
              <thead className="bg-gray-50 border-b"><tr>
                <th className="table-th">Name</th><th className="table-th">Start</th>
                <th className="table-th">End</th><th className="table-th">Campus</th>
                <th className="table-th">Course</th><th className="table-th">Actions</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-100">
                {batches.map((b) => (
                  <tr key={b.id} className="hover:bg-gray-50">
                    <td className="table-td font-medium">{b.name}</td>
                    <td className="table-td">{b.start_date}</td>
                    <td className="table-td text-gray-500">{b.end_date || "—"}</td>
                    <td className="table-td">{campuses.find((x) => x.id === b.campus_id)?.name || "—"}</td>
                    <td className="table-td">{courses.find((x) => x.id === b.course_id)?.name || "—"}</td>
                    <td className="table-td"><div className="flex gap-1">
                      <button onClick={() => openEdit(b)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500"><Pencil className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(b.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400"><Trash2 className="w-3.5 h-3.5" /></button>
                    </div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-semibold mb-4">
              {editItem ? "Edit" : "Create"} {tab.slice(0, -1).charAt(0).toUpperCase() + tab.slice(0, -1).slice(1)}
            </h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {tab === "campuses" && (<>
                <div><label className="label">Name *</label><input className="input" {...register("name", { required: true })} /></div>
                <div><label className="label">Code (e.g. KHI) *</label><input className="input" maxLength={10} {...register("code", { required: true })} /></div>
                <div><label className="label">City *</label><input className="input" {...register("city", { required: true })} /></div>
                <div><label className="label">Address</label><input className="input" {...register("address")} /></div>
                <div><label className="label">Phone</label><input className="input" {...register("phone")} /></div>
              </>)}
              {tab === "courses" && (<>
                <div><label className="label">Name *</label><input className="input" {...register("name", { required: true })} /></div>
                <div><label className="label">Code *</label><input className="input" {...register("code", { required: true })} /></div>
                <div><label className="label">Campus *</label>
                  <select className="input" {...register("campus_id", { required: true })}>
                    <option value="">Select Campus</option>
                    {campuses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div><label className="label">Duration (months)</label><input type="number" className="input" {...register("duration_months")} /></div>
                <div><label className="label">Description</label><textarea className="input resize-none" rows={2} {...register("description")} /></div>
              </>)}
              {tab === "batches" && (<>
                <div><label className="label">Batch Name *</label><input className="input" {...register("name", { required: true })} /></div>
                <div><label className="label">Campus *</label>
                  <select className="input" {...register("campus_id", { required: true })}>
                    <option value="">Select Campus</option>
                    {campuses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div><label className="label">Course *</label>
                  <select className="input" {...register("course_id", { required: true })}>
                    <option value="">Select Course</option>
                    {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div><label className="label">Start Date *</label><input type="date" className="input" {...register("start_date", { required: true })} /></div>
                <div><label className="label">End Date</label><input type="date" className="input" {...register("end_date")} /></div>
              </>)}
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="btn-primary">{isSubmitting ? "Saving..." : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
