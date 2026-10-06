import { apiFetch, buildQuery } from "@/lib/api-client";

export interface Scholarship {
  id: string;
  university_id: string;
  course_id?: string;
  name: string;
  amount?: string;
  eligibility?: string;
  deadline?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ScholarshipPayload {
  name: string;
  course_id?: string;
  amount?: string;
  eligibility?: string;
  deadline?: string;
  is_active?: boolean;
}

export interface ScholarshipListResponse {
  items: Scholarship[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const listScholarships = (params?: { is_active?: boolean; search?: string; page?: number; page_size?: number }) =>
  apiFetch<ScholarshipListResponse>(
    `/api/v1/scholarships/${buildQuery({ ...params, is_active: params?.is_active === undefined ? undefined : String(params.is_active) })}`,
    { method: "GET" },
  );

export const createScholarship = (data: ScholarshipPayload) =>
  apiFetch<Scholarship>("/api/v1/scholarships/", { method: "POST", body: JSON.stringify(data) });

export const updateScholarship = (id: string, data: Partial<ScholarshipPayload>) =>
  apiFetch<Scholarship>(`/api/v1/scholarships/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteScholarship = (id: string) =>
  apiFetch<void>(`/api/v1/scholarships/${id}`, { method: "DELETE" });
