"use client";
import { useEffect, useState, useCallback } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { studentApi, campusApi, batchApi, courseApi } from "@/lib/api";
import { Student, Campus, Batch, Course } from "@/types";
import { formatDate } from "@/utils";
import toast from "react-hot-toast";
import { Plus, Search, Download, QrCode, CreditCard, Trash2, Pencil, Eye } from "lucide-react";
import StudentModal from "@/components/forms/StudentModal";
import StudentDetailModal from "@/components/forms/StudentDetailModal";

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCampus, setSelectedCampus] = useState("");
  const [selectedBatch, setSelectedBatch] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editStudent, setEditStudent] = useState<Student | null>(null);
  const [viewStudent, setViewStudent] = useState<Student | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const fetchStudents = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: PAGE_SIZE };
      if (search) params.search = search;
      if (selectedCampus) params.campus_id = Number(selectedCampus);
      if (selectedBatch) params.batch_id = Number(selectedBatch);
      const res = await studentApi.list(params);
      setStudents(res.data.items || res.data);
      setTotal(res.data.total ?? res.data.length);
    } catch {
      toast.error("Failed to load students");
    } finally {
      setLoading(false);
    }
  }, [search, selectedCampus, selectedBatch, page]);

  useEffect(() => {
    campusApi.list().then((r) => setCampuses(r.data));
    batchApi.list().then((r) => setBatches(r.data));
    courseApi.list().then((r) => setCourses(r.data));
  }, []);

  useEffect(() => { fetchStudents(); }, [fetchStudents]);

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this student? This cannot be undone.")) return;
    try {
      await studentApi.delete(id);
      toast.success("Student deleted");
      fetchStudents();
    } catch {
      toast.error("Failed to delete student");
    }
  };

  const handleGenerateIdCard = async (id: number) => {
    try {
      await studentApi.generateIdCard(id);
      toast.success("ID card generated");
      window.open(studentApi.downloadIdCard(id), "_blank");
    } catch {
      toast.error("Failed to generate ID card");
    }
  };

  const getCampusName = (id: number) => campuses.find((c) => c.id === id)?.name || "—";
  const getBatchName = (id: number) => batches.find((b) => b.id === id)?.name || "—";
  const getCourseName = (id: number) => courses.find((c) => c.id === id)?.name || "—";

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Students</h1>
          <p className="text-gray-500 text-sm mt-1">{total} total students</p>
        </div>
        <button onClick={() => { setEditStudent(null); setShowModal(true); }} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Student
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              className="input pl-9"
              placeholder="Search name, ID, email..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />
          </div>
          <select className="input w-auto" value={selectedCampus} onChange={(e) => { setSelectedCampus(e.target.value); setPage(1); }}>
            <option value="">All Campuses</option>
            {campuses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select className="input w-auto" value={selectedBatch} onChange={(e) => { setSelectedBatch(e.target.value); setPage(1); }}>
            <option value="">All Batches</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="table-th">Student ID</th>
                <th className="table-th">Name</th>
                <th className="table-th">Campus</th>
                <th className="table-th">Course</th>
                <th className="table-th">Batch</th>
                <th className="table-th">Enrolled</th>
                <th className="table-th">Status</th>
                <th className="table-th">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan={8} className="table-td text-center py-12 text-gray-400">Loading...</td></tr>
              ) : students.length === 0 ? (
                <tr><td colSpan={8} className="table-td text-center py-12 text-gray-400">No students found</td></tr>
              ) : students.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                  <td className="table-td">
                    <span className="font-mono text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded font-medium">{s.student_id}</span>
                  </td>
                  <td className="table-td">
                    <div className="flex items-center gap-2">
                      {s.photo_path ? (
                        <img src={`${process.env.NEXT_PUBLIC_API_URL}/storage/${s.photo_path}`}
                          className="w-7 h-7 rounded-full object-cover" alt="" />
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 text-xs font-bold">
                          {s.full_name.charAt(0)}
                        </div>
                      )}
                      <span className="font-medium">{s.full_name}</span>
                    </div>
                  </td>
                  <td className="table-td text-gray-500">{getCampusName(s.campus_id)}</td>
                  <td className="table-td text-gray-500">{getCourseName(s.course_id)}</td>
                  <td className="table-td text-gray-500">{getBatchName(s.batch_id)}</td>
                  <td className="table-td text-gray-500">{formatDate(s.enrollment_date)}</td>
                  <td className="table-td">
                    <span className={`badge ${s.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                      {s.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="table-td">
                    <div className="flex items-center gap-1">
                      <button onClick={() => setViewStudent(s)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500" title="View">
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => { setEditStudent(s); setShowModal(true); }} className="p-1.5 hover:bg-gray-100 rounded text-gray-500" title="Edit">
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <a onClick={()=>{fetch(studentApi.getQR(s.id),{headers:{Authorization:"Bearer "+localStorage.getItem("access_token")}}).then(r=>r.blob()).then(b=>{const u=URL.createObjectURL(b);const a=document.createElement("a");a.href=u;a.download=s.student_id+"_qr.png";a.click();URL.revokeObjectURL(u)})}} className="p-1.5 hover:bg-gray-100 rounded text-gray-500" title="QR Code">
                        <QrCode className="w-3.5 h-3.5" />
                      </a>
                      <button onClick={() => handleGenerateIdCard(s.id)} className="p-1.5 hover:bg-gray-100 rounded text-gray-500" title="ID Card">
                        <CreditCard className="w-3.5 h-3.5" />
                      </button>
                      <button onClick={() => handleDelete(s.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400" title="Delete">
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > PAGE_SIZE && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, total)} of {total}
            </p>
            <div className="flex gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary py-1 px-3 text-sm disabled:opacity-40">Previous</button>
              <button disabled={page * PAGE_SIZE >= total} onClick={() => setPage(p => p + 1)} className="btn-secondary py-1 px-3 text-sm disabled:opacity-40">Next</button>
            </div>
          </div>
        )}
      </div>

      {showModal && (
        <StudentModal
          student={editStudent}
          campuses={campuses}
          batches={batches}
          courses={courses}
          onClose={() => setShowModal(false)}
          onSaved={() => { setShowModal(false); fetchStudents(); }}
        />
      )}
      {viewStudent && (
        <StudentDetailModal
          student={viewStudent}
          campuses={campuses}
          batches={batches}
          courses={courses}
          onClose={() => setViewStudent(null)}
          onRefresh={fetchStudents}
        />
      )}
    </AppLayout>
  );
}
