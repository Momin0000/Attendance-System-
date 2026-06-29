"use client";
import { useRef, useState } from "react";
import { studentApi } from "@/lib/api";
import { Student, Campus, Batch, Course } from "@/types";
import { formatDate } from "@/utils";
import toast from "react-hot-toast";
import { X, Upload, QrCode, CreditCard, Download } from "lucide-react";

interface Props {
  student: Student;
  campuses: Campus[];
  batches: Batch[];
  courses: Course[];
  onClose: () => void;
  onRefresh: () => void;
}

export default function StudentDetailModal({ student, campuses, batches, courses, onClose, onRefresh }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [generatingCard, setGeneratingCard] = useState(false);

  const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const campus = campuses.find((c) => c.id === student.campus_id);
  const batch = batches.find((b) => b.id === student.batch_id);
  const course = courses.find((c) => c.id === student.course_id);

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await studentApi.uploadPhoto(student.id, file);
      toast.success("Photo uploaded");
      onRefresh();
    } catch {
      toast.error("Photo upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleIdCard = async () => {
    setGeneratingCard(true);
    try {
      await studentApi.generateIdCard(student.id);
      toast.success("ID card ready!");
      fetch(studentApi.downloadIdCard(student.id), {headers:{Authorization:"Bearer "+localStorage.getItem("access_token")||""} }).then(r=>r.blob()).then(b=>{const u=URL.createObjectURL(b);const a=document.createElement("a");a.href=u;a.download=student.student_id+"_idcard.pdf";a.click();URL.revokeObjectURL(u)});
    } catch {
      toast.error("ID card generation failed");
    } finally {
      setGeneratingCard(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-lg font-semibold">Student Profile</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg"><X className="w-4 h-4" /></button>
        </div>

        <div className="p-5">
          {/* Photo + Basic */}
          <div className="flex gap-4 mb-5">
            <div className="relative">
              {student.photo_path ? (
                <img src={`${BASE}/storage/${student.photo_path}`} className="w-20 h-20 rounded-xl object-cover border" alt="" />
              ) : (
                <div className="w-20 h-20 rounded-xl bg-primary-100 flex items-center justify-center text-3xl font-bold text-primary-400">
                  {student.full_name.charAt(0)}
                </div>
              )}
              <button
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                className="absolute -bottom-2 -right-2 bg-white border shadow rounded-full p-1 hover:bg-gray-50"
                title="Upload photo"
              >
                <Upload className="w-3 h-3 text-gray-600" />
              </button>
              <input ref={fileRef} type="file" accept="image/jpeg,image/png" className="hidden" onChange={handlePhotoUpload} />
            </div>
            <div>
              <p className="font-bold text-lg text-gray-900">{student.full_name}</p>
              <p className="text-xs font-mono bg-primary-50 text-primary-700 px-2 py-0.5 rounded inline-block mt-1">{student.student_id}</p>
              <p className="text-sm text-gray-500 mt-1">{student.email || "—"}</p>
              <span className={`badge mt-1 ${student.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                {student.is_active ? "Active" : "Inactive"}
              </span>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm mb-5">
            {[
              ["Father Name", student.father_name],
              ["Phone", student.phone],
              ["CNIC", student.cnic],
              ["Gender", student.gender],
              ["DOB", formatDate(student.date_of_birth || "")],
              ["Enrolled", formatDate(student.enrollment_date)],
              ["Campus", campus?.name],
              ["Course", course?.name],
              ["Batch", batch?.name],
              ["Address", student.address],
            ].map(([label, value]) => (
              <div key={label}>
                <p className="text-gray-400 text-xs">{label}</p>
                <p className="text-gray-800 font-medium">{value || "—"}</p>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-2 flex-wrap">
            <a onClick={()=>{fetch(studentApi.getQR(student.id),{headers:{Authorization:"Bearer "+localStorage.getItem("access_token")}}).then(r=>r.blob()).then(b=>{const u=URL.createObjectURL(b);const a=document.createElement("a");a.href=u;a.download=student.student_id+"_qr.png";a.click();URL.revokeObjectURL(u)})}}
              className="btn-secondary flex items-center gap-2 text-sm py-1.5 px-3">
              <QrCode className="w-4 h-4" /> QR Code
            </a>
            <button onClick={handleIdCard} disabled={generatingCard}
              className="btn-primary flex items-center gap-2 text-sm py-1.5 px-3">
              <CreditCard className="w-4 h-4" /> {generatingCard ? "Generating..." : "Generate ID Card"}
            </button>

          </div>
        </div>
      </div>
    </div>
  );
}
