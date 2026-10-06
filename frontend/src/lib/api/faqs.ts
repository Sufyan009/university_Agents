import { apiFetch, buildQuery } from "@/lib/api-client";

export interface FAQ {
  id: string;
  university_id: string;
  question: string;
  answer: string;
  category?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FAQPayload {
  question: string;
  answer: string;
  category?: string;
  is_active?: boolean;
}

export interface FAQListResponse {
  items: FAQ[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const listFaqs = (params?: { category?: string; is_active?: boolean; search?: string; page?: number; page_size?: number }) =>
  apiFetch<FAQListResponse>(
    `/api/v1/faqs/${buildQuery({ ...params, is_active: params?.is_active === undefined ? undefined : String(params.is_active) })}`,
    { method: "GET" },
  );

export const createFaq = (data: FAQPayload) =>
  apiFetch<FAQ>("/api/v1/faqs/", { method: "POST", body: JSON.stringify(data) });

export const updateFaq = (id: string, data: Partial<FAQPayload>) =>
  apiFetch<FAQ>(`/api/v1/faqs/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteFaq = (id: string) =>
  apiFetch<void>(`/api/v1/faqs/${id}`, { method: "DELETE" });
