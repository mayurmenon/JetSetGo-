export interface ScrapeRequest {
  destination: string;
  start_date: string;
  end_date: string;
  budget: "Budget" | "Moderate" | "Luxury";
  origin_city?: string;
}

export interface ScrapeResponse {
  job_id: string;
  status: string;
  result?: unknown;
}

export interface AgentStatus {
  agent_name: string;
  status: "running" | "completed" | "error";
  message: string;
}

export interface StreamEvent {
  event: string;
  data: AgentStatus | string;
}
