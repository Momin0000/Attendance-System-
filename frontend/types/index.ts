export interface User {
  id: number;
  email: string;
  full_name: string;
  role: "super_admin" | "campus_admin" | "teacher" | "attendance_operator" | "student";
  campus_id: number | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Campus {
  id: number;
  name: string;
  code: string;
  city: string;
  address?: string;
  phone?: string;
  is_active: boolean;
}

export interface Course {
  id: number;
  name: string;
  code: string;
  description?: string;
  duration_months?: number;
  campus_id: number;
  is_active: boolean;
}

export interface Batch {
  id: number;
  name: string;
  start_date: string;
  end_date?: string;
  campus_id: number;
  course_id: number;
  is_active: boolean;
}

export interface Student {
  id: number;
  student_id: string;
  full_name: string;
  father_name?: string;
  cnic?: string;
  phone?: string;
  email?: string;
  gender?: "male" | "female" | "other";
  date_of_birth?: string;
  address?: string;
  photo_path?: string;
  campus_id: number;
  course_id: number;
  batch_id: number;
  enrollment_date: string;
  is_active: boolean;
  created_at: string;
  campus?: Campus;
  course?: Course;
  batch?: Batch;
}

export interface AttendanceRecord {
  id: number;
  student_db_id: number;
  student_id_code: string;
  campus_id: number;
  batch_id: number;
  attendance_date: string;
  check_in_time: string;
  status: "present" | "absent" | "late";
  notes?: string;
  student?: Student;
}

export interface AttendanceSummary {
  student_id: number;
  student_name: string;
  student_code: string;
  total_classes: number;
  present: number;
  absent: number;
  late: number;
  percentage: number;
}

export interface DashboardStats {
  total_students: number;
  active_students: number;
  total_campuses: number;
  total_batches: number;
  total_courses: number;
  today_attendance_percentage: number;
  weekly_attendance_trend: { date: string; present: number; total: number; percentage: number }[];
  campus_wise_stats: {
    campus_id: number;
    campus_name: string;
    total_students: number;
    active_students: number;
    total_batches: number;
    avg_attendance_percentage: number;
  }[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type Role = User["role"];
