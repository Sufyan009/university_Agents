import { apiFetch, buildQuery } from "@/lib/api-client";

export interface Course {
  id: string;
  university_id: string;
  name: string;
  degree_type?: string;
  description?: string;
  duration?: string;
  fee_structure?: Record<string, unknown>;
  admission_requirements?: string;
  created_at: string;
  updated_at: string;
}

export interface CoursePayload {
  name: string;
  degree_type?: string;
  description?: string;
  duration?: string;
  fee_structure?: Record<string, unknown>;
  admission_requirements?: string;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const listCourses = (params?: { degree_type?: string; search?: string; page?: number; page_size?: number }) =>
  apiFetch<CourseListResponse>(`/api/v1/courses/${buildQuery({ ...params })}`, { method: "GET" });

export const getCourse = (id: string) =>
  apiFetch<Course>(`/api/v1/courses/${id}`, { method: "GET" });

export const createCourse = (data: CoursePayload) =>
  apiFetch<Course>("/api/v1/courses/", { method: "POST", body: JSON.stringify(data) });

export const updateCourse = (id: string, data: Partial<CoursePayload>) =>
  apiFetch<Course>(`/api/v1/courses/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteCourse = (id: string) =>
  apiFetch<void>(`/api/v1/courses/${id}`, { method: "DELETE" });
