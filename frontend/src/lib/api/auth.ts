import { apiFetch } from "@/lib/api-client";

export interface LoginRequest {
  email: string;
  password: string;
}

export type AppRole = "admin" | "owner" | "manager" | "operator";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: AppRole;
  permissions: string[];
}

export const adminLogin = (data: LoginRequest) =>
  apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const universityLogin = (data: LoginRequest) =>
  apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });

export interface RegisterRequest {
  email: string;
  password: string;
  name?: string;
  phone?: string;
  role: AppRole;
  university_name: string;
}

export const registerUser = (data: RegisterRequest) =>
  apiFetch<UserProfile>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });

export function saveToken(token: string) {
  localStorage.setItem("access_token", token);
}

export function clearToken() {
  localStorage.removeItem("access_token");
}

export function clearRole() {
  localStorage.removeItem("user_role");
}

export function clearPermissions() {
  localStorage.removeItem("user_permissions");
}

export function logout() {
  clearToken();
  clearRole();
  clearPermissions();
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function saveRole(role: AppRole) {
  localStorage.setItem("user_role", role);
}

export function getRole(): AppRole | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("user_role") as AppRole | null;
}

export function savePermissions(permissions: string[]) {
  localStorage.setItem("user_permissions", JSON.stringify(permissions));
}

export function getPermissions(): string[] {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem("user_permissions");
  if (!stored) return [];
  try {
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed)
      ? parsed.filter((item): item is string => typeof item === "string")
      : [];
  } catch {
    return [];
  }
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  phone?: string;
  role: AppRole;
  is_active: boolean;
  university_id?: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateUserRequest {
  name?: string;
  phone?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export const getUserProfile = () =>
  apiFetch<UserProfile>("/api/v1/auth/me", { method: "GET" });

export const updateUserProfile = (data: UpdateUserRequest) =>
  apiFetch<UserProfile>("/api/v1/auth/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const changeUserPassword = (data: ChangePasswordRequest) =>
  apiFetch<{ message: string }>("/api/v1/auth/change-password", {
    method: "POST",
    body: JSON.stringify(data),
  });
