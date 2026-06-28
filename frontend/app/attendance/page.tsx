"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { attendanceApi, batchApi, campusApi } from "@/lib/api";
import { AttendanceRecord, Batch, Campus } from "@/types";
import { formatDateTime, getStatusBadgeClass } from "@/utils";
import toast from "react-hot-toast";
import { ScanLine, Plus, RefreshCw, Trash2 } from "lucide-react";
import { Html5QrcodeScanner } from "html5-qrcode";

export default function AttendancePage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [selectedBatch, setSelectedBatch] = useState("");
  const [showManual, setShowManual] = useState(false);
  const [manualStudentId, setManualStudentId] = useState("");
  const [manualStatus, setManualStatus] = useState("present");
  const [manualDate, setManualDate] = useState(new Date().toISOString().slice(0, 10));
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);
  const scannerDivId = "qr-reader";

  const fetchRecords = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { attendance_date: date };
      if (selectedBatch) params.batch_id = Number(selectedBatch);
      const res = await attendanceApi.daily(params);
      setRecords(res.data);
    } catch {
      toast.error("Failed to load attendance");
    } finally {
      setLoading(false);
    }
  }, [date, selectedBatch]);

  useEffect(() => {
    campusApi.list().then((r) => setCampuses(r.data));
    batchApi.list().then((r) => setBatches(r.data));
  }, []);

  useEffect(() => { fetchRecords(); }, [fetchRecords]);

  useEffect(() => {
    if (scanning) {
      setTimeout(() => {
        scannerRef.current = new Html5QrcodeScanner(scannerDivId, { fps: 10, qrbox: 250 }, false);
        scannerRef.current.render(
          async (decodedText) => {
            scannerRef.current?.pause(true);
            try {
              await attendanceApi.scanQR(decodedText);
              toast.success("✅ Attendance marked!");
              fetchRecords();
            } catch (err: any) {
              toast.error(err.response?.data?.detail || "Scan failed");
            } finally {
              setTimeout(() => scannerRef.current?.resume(), 2000);
            }
          },
          (err) => {}
        );
      }, 200);
    } else {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(() => {});
        scannerRef.current = null;
      }
    }
    return () => {
      if (scannerRef.current) scannerRef.current.clear().catch(() => {});
    };
  }, [scanning, fetchRecords]);

  const handleManualSubmit = async () => {
    if (!manualStudentId.trim()) { toast.error("Enter a student ID"); return; }
    try {
      await attendanceApi.markManual({
        student_id_code: manualStudentId.trim(),
        attendance_date: manualDate,
        status: manualStatus,
      });
      toast.success("Attendance marked manually");
      setShowManual(false);
      setManualStudentId("");
      fetchRecords();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to mark attendance");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this attendance record?")) return;
    try {
      await attendanceApi.delete(id);
      toast.success("Record deleted");
      fetchRecords();
    } catch {
      toast.error("Failed to delete");
    }
  };

  const presentCount = records.filter((r) => r.status === "present").length;
  const absentCount = records.filter((r) => r.status === "absent").length;

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Attendance</h1>
          <p className="text-gray-500 text-sm mt-1">{records.length} records · {presentCount} present · {absentCount} absent</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowManual(true)} className="btn-secondary flex items-center gap-2 text-sm">
            <Plus className="w-4 h-4" /> Manual Entry
          </button>
          <button onClick={() => setScanning((s) => !s)}
            className={`flex items-center gap-2 text-sm font-semibold py-2 px-4 rounded-lg transition-colors ${scanning ? "bg-red-600 hover:bg-red-700 text-white" : "btn-primary"}`}>
            <ScanLine className="w-4 h-4" /> {scanning ? "Stop Scanner" : "Scan QR"}
          </button>
        </div>
      </div>

      {/* QR Scanner */}
      {scanning && (
        <div className="card mb-6">
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            <ScanLine className="w-4 h-4 text-primary-600" /> QR Code Scanner
          </h2>
          <div id={scannerDivId} className="max-w-sm mx-auto" />
        </div>
      )}

      {/* Filters */}
      <div className="card mb-4">
        <div className="flex flex-wrap gap-3 items-center">
          <div>
            <label className="label">Date</label>
            <input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div>
            <label className="label">Batch</label>
            <select className="input" value={selectedBatch} onChange={(e) => setSelectedBatch(e.target.value)}>
              <option value="">All Batches</option>
              {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </div>
          <button onClick={fetchRecords} className="btn-secondary flex items-center gap-2 text-sm self-end">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="table-th">Student ID</th>
                <th className="table-th">Date</th>
                <th className="table-th">Check-In</th>
                <th className="table-th">Status</th>
                <th className="table-th">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr><td colSpan={5} className="table-td text-center py-12 text-gray-400">Loading...</td></tr>
              ) : records.length === 0 ? (
                <tr><td colSpan={5} className="table-td text-center py-12 text-gray-400">No attendance records for this date</td></tr>
              ) : records.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="table-td font-mono text-xs font-semibold text-primary-700">{r.student_id_code}</td>
                  <td className="table-td">{r.attendance_date}</td>
                  <td className="table-td text-gray-500">{r.check_in_time ? formatDateTime(r.check_in_time) : "—"}</td>
                  <td className="table-td">
                    <span className={`badge ${getStatusBadgeClass(r.status)}`}>{r.status}</span>
                  </td>
                  <td className="table-td">
                    <button onClick={() => handleDelete(r.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Entry Modal */}
      {showManual && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-semibold mb-4">Manual Attendance Entry</h2>
            <div className="space-y-4">
              <div>
                <label className="label">Student ID (e.g. BQ-KHI-000001)</label>
                <input className="input" value={manualStudentId} onChange={(e) => setManualStudentId(e.target.value)} placeholder="BQ-KHI-000001" />
              </div>
              <div>
                <label className="label">Date</label>
                <input type="date" className="input" value={manualDate} onChange={(e) => setManualDate(e.target.value)} />
              </div>
              <div>
                <label className="label">Status</label>
                <select className="input" value={manualStatus} onChange={(e) => setManualStatus(e.target.value)}>
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                  <option value="late">Late</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-5">
              <button onClick={() => setShowManual(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleManualSubmit} className="btn-primary">Mark Attendance</button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
