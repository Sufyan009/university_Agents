import { apiFetch } from "@/lib/api-client";

export interface Deadline {
  label?: string;
  date?: string;
}

export interface AdmissionInfo {
  id: string;
  university_id: string;
  criteria?: string;
  eligibility?: string;
  deadlines?: Deadline[];
  application_process?: string;
  required_documents?: string[];
  scholarship_info?: string;
  created_at: string;
  updated_at: string;
}

export interface AdmissionPayload {
  criteria?: string;
  eligibility?: string;
  deadlines?: Deadline[];
  application_process?: string;
  required_documents?: string[];
  scholarship_info?: string;
}

export const getAdmissionInfo = () =>
  apiFetch<AdmissionInfo>("/api/v1/admissions/", { method: "GET" });

export const createAdmissionInfo = (data: AdmissionPayload) =>
  apiFetch<AdmissionInfo>("/api/v1/admissions/", { method: "POST", body: JSON.stringify(data) });

export const upsertAdmissionInfo = (data: AdmissionPayload) =>
  apiFetch<AdmissionInfo>("/api/v1/admissions/", { method: "PUT", body: JSON.stringify(data) });

export const deleteAdmissionInfo = () =>
  apiFetch<void>("/api/v1/admissions/", { method: "DELETE" });
