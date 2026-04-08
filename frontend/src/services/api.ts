import axios from "axios";
import type { AgentStatus, ScrapeRequest, ScrapeResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function submitScrapeJob(
  data: ScrapeRequest
): Promise<{ job_id: string }> {
  const response = await api.post<{ job_id: string }>("/api/scrape", data);
  return response.data;
}

export function streamScrapeProgress(
  jobId: string,
  onMessage: (event: AgentStatus) => void,
  onError?: (error: unknown) => void,
  onComplete?: () => void
): EventSource {
  const streamUrl = `${API_BASE_URL}/api/scrape/${jobId}/stream`;
  const source = new EventSource(streamUrl);

  source.onmessage = (messageEvent) => {
    try {
      const parsed = JSON.parse(messageEvent.data) as AgentStatus;
      onMessage(parsed);

      if (parsed.status === "completed" && parsed.agent_name === "Orchestrator") {
        onComplete?.();
        source.close();
      }
      if (parsed.status === "error") {
        onError?.(new Error(parsed.message || "Stream reported an error status"));
      }
    } catch (error) {
      onError?.(error);
    }
  };

  source.onerror = (error) => {
    onError?.(error);
    source.close();
  };

  return source;
}

export async function fetchScrapeResult(jobId: string): Promise<ScrapeResponse> {
  const response = await api.get<ScrapeResponse>(`/api/scrape/${jobId}/result`);
  return response.data;
}
