import { apiFetch, buildQuery } from "@/lib/api-client";
import type { University, UniversityPayload } from "@/lib/api/university";

export interface AdminUniversityListResponse {
  items: University[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const adminListUniversities = (params?: { search?: string; page?: number; page_size?: number }) =>
  apiFetch<AdminUniversityListResponse>(`/api/v1/admin/universities/${buildQuery({ ...params })}`, { method: "GET" });

export const adminGetUniversity = (id: string) =>
  apiFetch<University>(`/api/v1/admin/universities/${id}`, { method: "GET" });

export const adminCreateUniversity = (data: UniversityPayload) =>
  apiFetch<University>("/api/v1/admin/universities/", { method: "POST", body: JSON.stringify(data) });

export const adminUpdateUniversity = (id: string, data: Partial<UniversityPayload>) =>
  apiFetch<University>(`/api/v1/admin/universities/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const adminDeleteUniversity = (id: string) =>
  apiFetch<void>(`/api/v1/admin/universities/${id}`, { method: "DELETE" });
