import { apiFetch } from "@/lib/api-client";

// ── University profile (tenant owner scope) ──────────────────────────────────
export interface Location {
  address?: string;
  city?: string;
  state?: string;
  postcode?: string;
  country?: string;
}

export interface ContactInfo {
  phone?: string;
  email?: string;
  fax?: string;
}

export interface AdmissionOffice {
  name?: string;
  email?: string;
  phone?: string;
  hours?: string;
}

export interface University {
  id: string;
  admin_id?: string;
  name: string;
  description?: string;
  location?: Location;
  contact_info?: ContactInfo;
  admission_office?: AdmissionOffice;
  phone?: string;
  website?: string;
  created_at: string;
  updated_at: string;
}

export interface UniversityPayload {
  name: string;
  description?: string;
  location?: Location;
  contact_info?: ContactInfo;
  admission_office?: AdmissionOffice;
  phone?: string;
  website?: string;
}

export const getUniversityProfile = () =>
  apiFetch<University>("/api/v1/university/profile", { method: "GET" });

export const createUniversityProfile = (data: UniversityPayload) =>
  apiFetch<University>("/api/v1/university/profile", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateUniversityProfile = (data: Partial<UniversityPayload>) =>
  apiFetch<University>("/api/v1/university/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });

// ── Agent config ─────────────────────────────────────────────────────────────
export interface VoiceConfig {
  voice_id: string;
  speed: number;
  language: string;
}

export interface AgentConfig {
  id: string;
  university_id: string;
  agent_name: string;
  personality: string;
  greeting_message: string;
  special_instructions?: string;
  voice_config: VoiceConfig;
  context_text?: string;
  enable_admissions: boolean;
  enable_courses: boolean;
  enable_scholarships: boolean;
  enable_faq: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentConfigPayload {
  agent_name?: string;
  personality?: string;
  greeting_message?: string;
  special_instructions?: string;
  voice_config?: VoiceConfig;
  enable_admissions?: boolean;
  enable_courses?: boolean;
  enable_scholarships?: boolean;
  enable_faq?: boolean;
}

export const getAgentConfig = () =>
  apiFetch<AgentConfig>("/api/v1/university/config", { method: "GET" });

export const createAgentConfig = (data: AgentConfigPayload) =>
  apiFetch<AgentConfig>("/api/v1/university/config", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateAgentConfig = (data: AgentConfigPayload) =>
  apiFetch<AgentConfig>("/api/v1/university/config", {
    method: "PUT",
    body: JSON.stringify(data),
  });

// Voice options (mirrors the agent's config/models.py)
export const VOICE_OPTIONS = [
  { id: "gemma", label: "Gemma — British female", group: "Cartesia (British)" },
  { id: "lucy", label: "Lucy — British female", group: "Cartesia (British)" },
  { id: "victoria", label: "Victoria — British female", group: "Cartesia (British)" },
  { id: "evie", label: "Evie — British female", group: "Cartesia (British)" },
  { id: "jackqueline", label: "Jackqueline — American female", group: "Cartesia (American)" },
  { id: "cathy", label: "Cathy — American female", group: "Cartesia (American)" },
  { id: "dorothy", label: "Dorothy — American female", group: "Cartesia (American)" },
];

export const PERSONALITY_OPTIONS = [
  "friendly",
  "professional",
  "casual",
  "formal",
  "enthusiastic",
];
