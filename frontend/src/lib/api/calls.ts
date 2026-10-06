import { apiFetch, buildQuery } from "@/lib/api-client";

export interface CallSession {
  id: string;
  university_id: string;
  livekit_room_id: string;
  agent_type: string;
  status: string;
  caller_identity?: string;
  started_at: string;
  ended_at?: string;
  created_at: string;
}

export interface CallMessage {
  id: string;
  call_session_id: string;
  role: string;
  content: string;
  sequence: number;
  created_at: string;
}

export interface CallSessionDetail extends CallSession {
  messages: CallMessage[];
}

export const listCalls = (params?: { status?: string }) =>
  apiFetch<CallSession[]>(`/api/v1/calls/${buildQuery({ ...params })}`, { method: "GET" });

export const getCall = (id: string) =>
  apiFetch<CallSessionDetail>(`/api/v1/calls/${id}`, { method: "GET" });
