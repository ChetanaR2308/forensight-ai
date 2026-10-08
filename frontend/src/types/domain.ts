export type Role = "investigator" | "analyst" | "admin";

export interface CaseRecord {
  id: string;
  title: string;
  description: string;
  owner_id: string;
  collaborators: string[];
  created_at: string;
  updated_at: string;
}

export interface Observation {
  id: string;
  evidence_id: string;
  kind: string;
  value: string;
  status: string;
  source: string;
  confidence: number;
}

export interface Evidence {
  id: string;
  case_id: string;
  filename: string;
  size_bytes: number;
  sha256: string;
  processing_status: string;
  metadata: Record<string, unknown>;
}
