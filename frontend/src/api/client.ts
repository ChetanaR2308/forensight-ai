import { CaseRecord, Evidence } from "../types/domain";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", "Bearer " + token);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail || "Request failed");
  }

  return response.json() as Promise<T>;
}

export interface AuthResponse {
  access_token: string;
  role: "investigator" | "analyst" | "admin";
}

export const api = {
  login: (username: string, password: string) =>
    request<AuthResponse>("/auth/token", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  listCases: (token: string) => request<CaseRecord[]>("/cases", {}, token),
  createCase: (token: string, title: string, description: string) =>
    request<CaseRecord>(
      "/cases",
      {
        method: "POST",
        body: JSON.stringify({ title, description }),
      },
      token,
    ),
  listEvidence: (token: string, caseId: string) => request<Evidence[]>(`/cases/${caseId}/evidence`, {}, token),
  uploadEvidence: async (token: string, caseId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE}/cases/${caseId}/evidence`, {
      method: "POST",
      headers: { Authorization: "Bearer " + token },
      body: formData,
    });
    if (!response.ok) throw new Error("Upload failed");
    return response.json();
  },
  getTimeline: (token: string, caseId: string) => request<{ events: Array<{ id: string; description: string; timestamp: string; status: string }> }>(`/cases/${caseId}/evidence/timeline`, {}, token),
  queryCase: (token: string, caseId: string, question: string) =>
    request<{ result: { answer: string; status: string; citations: Array<{ evidence_id: string; source: string }> } }>(
      `/cases/${caseId}/investigation/query`,
      { method: "POST", body: JSON.stringify({ question }) },
      token,
    ),
  getReport: (token: string, caseId: string) => request<{ report: { summary: string; conflicts: string[]; evidence_gaps: string[]; suggested_next_actions: string[] } }>(`/cases/${caseId}/investigation/report`, {}, token),
};
