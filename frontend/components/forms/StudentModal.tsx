"use client";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { studentApi } from "@/lib/api";
import { Student, Campus, Batch, Course } from "@/types";
import toast from "react-hot-toast";
import { X } from "lucide-react";

interface Props {
  student: Student | null;
  campuses: Campus[];
  batches: Batch[];
  courses: Course[];
  onClose: () => void;
  onSaved: () => void;
}

interface FormData {
  full_name: string;
  father_name: string;
  cnic: string;
  phone: string;
  email: string;
  gender: string;
  date_of_birth: string;
  address: string;
  campus_id: number;
  course_id: number;
  batch_id: number;
  enrollment_date: string;
}

export default function StudentModal({ student, campuses, batches, courses, onClose, onSaved }: Props) {
  const { register, handleSubmit, reset, watch, formState: { errors, isSubmitting } } = useForm<FormData>();
  const selectedCampus = watch("campus_id");

  useEffect(() => {
    if (student) {
      reset({
        full_name: student.full_name,
        father_name: student.father_name || "",
        cnic: student.cnic || "",
        phone: student.phone || "",
        email: student.email || "",
        gender: student.gender || "",
        date_of_birth: student.date_of_birth || "",
        address: student.address || "",
        campus_id: student.campus_id,
        course_id: student.course_id,
        batch_id: student.batch_id,
        enrollment_date: student.enrollment_date,
      });
    } else {
      reset({ enrollment_date: new Date().toISOString().slice(0, 10) });
    }
  }, [student, reset]);

  const filteredBatches = batches.filter((b) => !selectedCampus || b.campus_id === Number(selectedCampus));
  const filteredCourses = courses.filter((c) => !selectedCampus || c.campus_id === Number(selectedCampus));

  const onSubmit = async (data: FormData) => {
    try {
      const payload = {
        ...data,
        campus_id: Number(data.campus_id),
        course_id: Number(data.course_id),
        batch_id: Number(data.batch_id),
      };
      if (student) {
        await studentApi.update(student.id, payload);
        toast.success("Student updated");
      } else {
        await studentApi.create(payload);
        toast.success("Student created");
      }
      onSaved();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to save student");
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold">{student ? "Edit Student" : "Add New Student"}</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg"><X className="w-4 h-4" /></button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Full Name *</label>
              <input className="input" {...register("full_name", { required: "Required" })} />
              {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message}</p>}
            </div>
            <div>
              <label className="label">Father Name</label>
              <input className="input" {...register("father_name")} />
            </div>
            <div>
              <label className="label">CNIC</label>
              <input className="input" placeholder="42101-1234567-1" {...register("cnic")} />
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" placeholder="03XX-XXXXXXX" {...register("phone")} />
            </div>
            <div>
              <label className="label">Email</label>
              <input className="input" type="email" {...register("email")} />
            </div>
            <div>
              <label className="label">Gender</label>
              <select className="input" {...register("gender")}>
                <option value="">Select</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="label">Date of Birth</label>
              <input className="input" type="date" {...register("date_of_birth")} />
            </div>
            <div>
              <label className="label">Enrollment Date *</label>
              <input className="input" type="date" {...register("enrollment_date", { required: "Required" })} />
            </div>
          </div>

          <div>
            <label className="label">Address</label>
            <textarea className="input resize-none" rows={2} {...register("address")} />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Campus *</label>
              <select className="input" {...register("campus_id", { required: "Required" })}>
                <option value="">Select</option>
                {campuses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              {errors.campus_id && <p className="text-red-500 text-xs mt-1">{errors.campus_id.message}</p>}
            </div>
            <div>
              <label className="label">Course *</label>
              <select className="input" {...register("course_id", { required: "Required" })}>
                <option value="">Select</option>
                {filteredCourses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              {errors.course_id && <p className="text-red-500 text-xs mt-1">{errors.course_id.message}</p>}
            </div>
            <div>
              <label className="label">Batch *</label>
              <select className="input" {...register("batch_id", { required: "Required" })}>
                <option value="">Select</option>
                {filteredBatches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
              {errors.batch_id && <p className="text-red-500 text-xs mt-1">{errors.batch_id.message}</p>}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="btn-primary">
              {isSubmitting ? "Saving..." : student ? "Update Student" : "Create Student"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
