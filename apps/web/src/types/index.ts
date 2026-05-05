export type DeviceStatus = "online" | "offline" | "unknown";
export type Severity = "critical" | "high" | "medium" | "low";
export type IncidentStatus = "open" | "investigating" | "resolved";

export interface Device {
  id: string;
  project_id: string;
  device_name: string;
  hardware_model: string | null;
  os_version: string | null;
  agent_version: string | null;
  status: DeviceStatus;
  last_seen_at: string | null;
  registered_at: string;
  created_at: string;
}

export interface Deployment {
  id: string;
  device_id: string;
  version: string;
  deployed_at: string;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface Incident {
  id: string;
  project_id: string;
  device_id: string;
  deployment_id: string | null;
  title: string;
  severity: Severity;
  status: IncidentStatus;
  trigger_type: string | null;
  root_cause_summary: string | null;
  analysis_json: Record<string, unknown> | null;
  started_at: string;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
  device_name?: string;
  deployment_version?: string;
  event_count?: number;
  metric_count?: number;
}

export interface IncidentListResponse {
  incidents: Incident[];
  total: number;
}

export interface EventLog {
  id: string;
  timestamp: string;
  level: string;
  source: string;
  message: string;
  metadata_json: Record<string, unknown> | null;
}

export interface MetricPoint {
  id: string;
  timestamp: string;
  metric_name: string;
  value: number;
  unit: string | null;
  labels_json: Record<string, unknown> | null;
}

export interface ProjectSummary {
  project_id: string;
  total_devices: number;
  online_devices: number;
  total_incidents: number;
}

export interface AnalysisResult {
  summary: string;
  probable_causes: Array<{
    cause: string;
    confidence: number;
    description: string;
    rule_id?: string;
  }>;
  evidence: Array<{
    signal: string;
    description: string;
    [key: string]: unknown;
  }>;
  suggested_steps: string[];
  metrics_analyzed: number;
  events_analyzed: number;
}
