import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401 → try refresh token → retry once → else logout
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        if (!refresh) throw new Error("No refresh token");
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refresh,
        });
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original);
      } catch {
        localStorage.clear();
        window.location.href = "/auth";
      }
    }
    return Promise.reject(error);
  }
);

// ---- AUTH ----
export const authApi = {
  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/auth/me"),
  changePassword: (current_password: string, new_password: string) =>
    api.put("/auth/change-password", { current_password, new_password }),
};

// ---- CAMPUSES ----
export const campusApi = {
  list: () => api.get("/campuses/"),
  get: (id: number) => api.get(`/campuses/${id}`),
  create: (data: object) => api.post("/campuses/", data),
  update: (id: number, data: object) => api.put(`/campuses/${id}`, data),
  delete: (id: number) => api.delete(`/campuses/${id}`),
};

// ---- COURSES ----
export const courseApi = {
  list: (campus_id?: number) =>
    api.get("/courses/", { params: campus_id ? { campus_id } : {} }),
  create: (data: object) => api.post("/courses/", data),
  update: (id: number, data: object) => api.put(`/courses/${id}`, data),
  delete: (id: number) => api.delete(`/courses/${id}`),
};

// ---- BATCHES ----
export const batchApi = {
  list: (campus_id?: number, course_id?: number) =>
    api.get("/batches/", { params: { campus_id, course_id } }),
  create: (data: object) => api.post("/batches/", data),
  update: (id: number, data: object) => api.put(`/batches/${id}`, data),
  delete: (id: number) => api.delete(`/batches/${id}`),
};

// ---- STUDENTS ----
export const studentApi = {
  list: (params?: object) => api.get("/students/", { params }),
  get: (id: number) => api.get(`/students/${id}`),
  getByStudentId: (student_id: string) => api.get(`/students/by-code/${student_id}`),
  create: (data: object) => api.post("/students/", data),
  update: (id: number, data: object) => api.put(`/students/${id}`, data),
  delete: (id: number) => api.delete(`/students/${id}`),
  uploadPhoto: (id: number, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post(`/students/${id}/photo`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getQR: (id: number) => `${BASE_URL}/students/${id}/qr`,
  generateIdCard: (id: number) => api.post(`/students/${id}/id-card`),
  downloadIdCard: (id: number) => `${BASE_URL}/students/${id}/id-card/download`,
};

// ---- ATTENDANCE ----
export const attendanceApi = {
  scanQR: (qr_data: string) => api.post("/attendance/scan", { qr_data }),
  markManual: (data: object) => api.post("/attendance/manual", data),
  daily: (params?: object) => api.get("/attendance/daily", { params }),
  studentHistory: (student_id: number, params?: object) =>
    api.get(`/attendance/student/${student_id}/history`, { params }),
  studentSummary: (student_id: number, params?: object) =>
    api.get(`/attendance/student/${student_id}/summary`, { params }),
  delete: (id: number) => api.delete(`/attendance/${id}`),
};

// ---- ANALYTICS ----
export const analyticsApi = {
  dashboard: () => api.get("/analytics/dashboard"),
  batch: (batch_id: number) => api.get(`/analytics/batch/${batch_id}`),
  lowAttendance: (threshold?: number, campus_id?: number) =>
    api.get("/analytics/low-attendance", { params: { threshold, campus_id } }),
};

// ---- REPORTS ----
export const reportsApi = {
  attendanceExcel: (params?: object) =>
    `${BASE_URL}/reports/attendance/excel?${new URLSearchParams(params as Record<string, string>)}`,
  attendanceCsv: (params?: object) =>
    `${BASE_URL}/reports/attendance/csv?${new URLSearchParams(params as Record<string, string>)}`,
  attendancePdf: (params?: object) =>
    `${BASE_URL}/reports/attendance/pdf?${new URLSearchParams(params as Record<string, string>)}`,
  studentsExcel: (params?: object) =>
    `${BASE_URL}/reports/students/excel?${new URLSearchParams(params as Record<string, string>)}`,
};

// ---- USERS ----
export const userApi = {
  list: (params?: object) => api.get("/users/", { params }),
  get: (id: number) => api.get(`/users/${id}`),
  create: (data: object) => api.post("/users/", data),
  update: (id: number, data: object) => api.put(`/users/${id}`, data),
  delete: (id: number) => api.delete(`/users/${id}`),
  resetPassword: (id: number, new_password: string) =>
    api.post(`/users/${id}/reset-password`, null, { params: { new_password } }),
};

export default api;
