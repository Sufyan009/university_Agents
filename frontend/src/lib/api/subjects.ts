import { apiFetch, buildQuery } from "@/lib/api-client";

export interface Subject {
  id: string;
  course_id: string;
  university_id: string;
  name: string;
  description?: string;
  credits?: number;
  prerequisites?: string;
  additional_info?: string;
  created_at: string;
  updated_at: string;
}

export interface SubjectPayload {
  course_id: string;
  name: string;
  description?: string;
  credits?: number;
  prerequisites?: string;
  additional_info?: string;
}

export interface SubjectListResponse {
  items: Subject[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const listSubjects = (params?: { course_id?: string; search?: string; page?: number; page_size?: number }) =>
  apiFetch<SubjectListResponse>(`/api/v1/subjects/${buildQuery({ ...params })}`, { method: "GET" });

export const getSubject = (id: string) =>
  apiFetch<Subject>(`/api/v1/subjects/${id}`, { method: "GET" });

export const createSubject = (data: SubjectPayload) =>
  apiFetch<Subject>("/api/v1/subjects/", { method: "POST", body: JSON.stringify(data) });

export const updateSubject = (id: string, data: Partial<Omit<SubjectPayload, "course_id">>) =>
  apiFetch<Subject>(`/api/v1/subjects/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteSubject = (id: string) =>
  apiFetch<void>(`/api/v1/subjects/${id}`, { method: "DELETE" });
