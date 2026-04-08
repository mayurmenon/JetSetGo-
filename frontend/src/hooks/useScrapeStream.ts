import { useCallback, useEffect, useRef, useState } from "react";

import {
  fetchScrapeResult,
  streamScrapeProgress,
  submitScrapeJob,
} from "../services/api";
import type { AgentStatus, ScrapeRequest } from "../types";

type ScrapeLifecycleStatus =
  | "idle"
  | "submitting"
  | "running"
  | "completed"
  | "error";

export function useScrapeStream() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<ScrapeLifecycleStatus>("idle");
  const [progressEvents, setProgressEvents] = useState<AgentStatus[]>([]);
  const [result, setResult] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);

  const streamRef = useRef<EventSource | null>(null);

  const closeStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
    }
  }, []);

  const getFriendlyStreamError = useCallback((streamError: unknown): string => {
    if (streamError instanceof Error && streamError.message) {
      return streamError.message;
    }
    return "Live progress connection was interrupted. We are checking the latest job result.";
  }, []);

  const reset = useCallback(() => {
    closeStream();
    setJobId(null);
    setStatus("idle");
    setProgressEvents([]);
    setResult(null);
    setError(null);
  }, [closeStream]);

  const startScrape = useCallback(
    async (request: ScrapeRequest): Promise<void> => {
      closeStream();
      setStatus("submitting");
      setError(null);
      setResult(null);
      setProgressEvents([]);

      try {
        const { job_id } = await submitScrapeJob(request);
        setJobId(job_id);
        setStatus("running");

        streamRef.current = streamScrapeProgress(
          job_id,
          (event) => {
            setProgressEvents((prev) => [...prev, event]);
            const eventStatus = event.status as string;
            if (eventStatus === "error" || eventStatus === "failed") {
              setStatus("error");
              setError(event.message || "Scraping pipeline reported an error.");
            }
          },
          async (streamError) => {
            try {
              const finalResult = await fetchScrapeResult(job_id);
              setResult(finalResult.result ?? null);
              if (finalResult.status === "completed") {
                setStatus("completed");
                setError(null);
                return;
              }
              if (finalResult.status === "failed" || finalResult.status === "error") {
                setStatus("error");
                setError(
                  (finalResult.result as { error?: string } | undefined)?.error ??
                    "The scrape job finished with an error. Please try again."
                );
                return;
              }
            } catch {
              // Fall back to stream error if result fetch also fails.
            }

            setStatus("error");
            setError(getFriendlyStreamError(streamError));
          },
          async () => {
            try {
              const finalResult = await fetchScrapeResult(job_id);
              setResult(finalResult.result ?? null);
              setStatus(finalResult.status === "completed" ? "completed" : "error");
              if (finalResult.status !== "completed") {
                setError(
                  (finalResult.result as { error?: string } | undefined)?.error ??
                    "Scrape did not complete successfully."
                );
              }
            } catch (fetchError) {
              setStatus("error");
              setError(
                fetchError instanceof Error
                  ? fetchError.message
                  : "Failed to fetch final scrape result."
              );
            } finally {
              closeStream();
            }
          }
        );
      } catch (submitError) {
        setStatus("error");
        setError(
          submitError instanceof Error
            ? submitError.message
            : "Unable to submit your scrape job right now. Please try again."
        );
      }
    },
    [closeStream, getFriendlyStreamError]
  );

  useEffect(() => {
    return () => {
      closeStream();
    };
  }, [closeStream]);

  return {
    jobId,
    status,
    progressEvents,
    result,
    error,
    startScrape,
    reset,
  };
}
