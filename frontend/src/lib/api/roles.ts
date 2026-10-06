import { apiFetch } from "@/lib/api-client";
import type { AppRole } from "@/lib/api/auth";

export interface UniversityUser {
  id: string;
  email: string;
  full_name: string;
  role: AppRole;
  is_active: boolean;
  created_at: string;
}

export interface UserListResponse {
  items: UniversityUser[];
  total: number;
}

export const listUsers = () =>
  apiFetch<UserListResponse>("/api/v1/roles/users/", { method: "GET" });

export const inviteUser = (data: { email: string; role: "owner" | "manager" | "operator" }) =>
  apiFetch<UniversityUser>("/api/v1/roles/users/invite", { method: "POST", body: JSON.stringify(data) });

export const updateUserRole = (userId: string, role: "owner" | "manager" | "operator") =>
  apiFetch<UniversityUser>(`/api/v1/roles/users/${userId}`, { method: "PATCH", body: JSON.stringify({ role }) });

export const removeUser = (userId: string) =>
  apiFetch<void>(`/api/v1/roles/users/${userId}`, { method: "DELETE" });

export interface PermissionEntry {
  permission: string;
  owner: boolean;
  manager: boolean;
  operator: boolean;
}

export const getPermissionsMatrix = () =>
  apiFetch<{ permissions: PermissionEntry[] }>("/api/v1/roles/permissions/", { method: "GET" });
