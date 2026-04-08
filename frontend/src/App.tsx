import { useEffect, useRef } from "react";
import toast from "react-hot-toast";

import { AgentStatusCard } from "./components/AgentStatusCard";
import { Layout } from "./components/Layout";
import { ProgressStream } from "./components/ProgressStream";
import { ResultViewer } from "./components/ResultViewer";
import { TripPlannerForm } from "./components/TripPlannerForm";
import { useScrapeStream } from "./hooks/useScrapeStream";

function App() {
  const { jobId, status, startScrape, progressEvents, result, error, reset } =
    useScrapeStream();
  const previousStatusRef = useRef(status);

  const showProgress = status === "running" || status === "completed";
  const showResult = status === "completed" && Boolean(result);
  const isBusy = status === "submitting" || status === "running";
  const itineraryMarkdown =
    typeof result === "string"
      ? result
      : result &&
        typeof result === "object" &&
        "itinerary" in result &&
        typeof (result as { itinerary?: unknown }).itinerary === "string"
      ? (result as { itinerary: string }).itinerary
      : result &&
        typeof result === "object" &&
        "markdown_report" in result &&
        typeof (result as { markdown_report?: unknown }).markdown_report === "string"
      ? (result as { markdown_report: string }).markdown_report
      : "";

  const copyItinerary = async () => {
    if (!itineraryMarkdown) {
      toast.error("No itinerary available to copy yet.");
      return;
    }
    try {
      await navigator.clipboard.writeText(itineraryMarkdown);
      toast.success("Itinerary copied to clipboard.");
    } catch {
      toast.error("Could not copy itinerary. Please copy manually.");
    }
  };

  useEffect(() => {
    const previousStatus = previousStatusRef.current;

    if (status === "running" && previousStatus === "submitting") {
      toast.success("Scrape job submitted successfully.");
    }

    if (status === "completed" && previousStatus !== "completed") {
      toast.success("Scrape completed. Result is ready.");
    }

    if (status === "error" && error && previousStatus !== "error") {
      toast.error(error);
    }

    previousStatusRef.current = status;
  }, [status, error]);

  return (
    <Layout>
      <main className="space-y-4">
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            ✈️ AI Travel Agent (Multi-Agent Trip Planner)
          </h2>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
            Plan your trip with coordinated specialist agents for flights, hotels,
            attractions, weather, and itinerary synthesis.
          </p>
        </section>

        <section className="grid gap-4 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <TripPlannerForm status={status} startScrape={startScrape} />
          </div>

          <div className="space-y-4 lg:col-span-8">
            {(isBusy || jobId) && (
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm text-slate-600 dark:text-slate-300">
                    Job: <span className="font-mono text-xs">{jobId ?? "pending..."}</span>
                  </p>
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${
                      status === "completed"
                        ? "bg-emerald-100 text-emerald-700"
                        : status === "error"
                        ? "bg-rose-100 text-rose-700"
                        : "bg-sky-100 text-sky-700"
                    }`}
                  >
                    {status === "submitting" ? "submitting job" : status}
                  </span>
                </div>
              </section>
            )}

            {error && (
              <section className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 shadow-sm">
                <p className="font-medium">Something went wrong</p>
                <p className="mt-1">{error}</p>
              </section>
            )}

            {showProgress && <ProgressStream events={progressEvents} />}

            {showProgress && <AgentStatusCard events={progressEvents} />}

            {showResult && (
              <>
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={copyItinerary}
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
                  >
                    Copy Itinerary
                  </button>
                </div>
                <ResultViewer result={result} />
              </>
            )}
          </div>
        </section>

        {(jobId || status === "completed" || status === "error") && (
          <div className="flex justify-end">
            <button
              type="button"
              onClick={() => {
                reset();
                toast("Ready for a new scrape.");
              }}
              disabled={isBusy}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              Start New Scrape
            </button>
          </div>
        )}
      </main>
    </Layout>
  );
}

export default App;
