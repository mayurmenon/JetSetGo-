import { CheckCircle2, Loader2, XCircle } from "lucide-react";

import type { AgentStatus } from "../types";

interface ProgressStreamProps {
  events: AgentStatus[];
}

function badgeClass(agentName: string): string {
  const classes = [
    "bg-sky-100 text-sky-700",
    "bg-violet-100 text-violet-700",
    "bg-emerald-100 text-emerald-700",
    "bg-amber-100 text-amber-700",
    "bg-rose-100 text-rose-700",
  ];
  let hash = 0;
  for (let i = 0; i < agentName.length; i += 1) {
    hash = (hash + agentName.charCodeAt(i)) % classes.length;
  }
  return classes[hash];
}

function StatusIcon({ status }: { status: AgentStatus["status"] }) {
  if (status === "running") {
    return <Loader2 className="h-4 w-4 animate-spin text-sky-600" />;
  }
  if (status === "completed") {
    return <CheckCircle2 className="h-4 w-4 text-emerald-600" />;
  }
  return <XCircle className="h-4 w-4 text-rose-600" />;
}

export function ProgressStream({ events }: ProgressStreamProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 text-lg font-semibold text-slate-900">Progress Timeline</h2>
      <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
        {events.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            No progress yet. Start a scrape job to see live updates.
          </p>
        ) : (
          events.map((event, index) => (
            <article
              key={`${event.agent_name}-${event.status}-${index}`}
              className="rounded-lg border border-slate-200 bg-slate-50 p-3"
            >
              <div className="mb-2 flex items-center justify-between gap-2">
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeClass(
                    event.agent_name
                  )}`}
                >
                  {event.agent_name}
                </span>
                <span className="inline-flex items-center gap-1 text-xs font-medium capitalize text-slate-700">
                  <StatusIcon status={event.status} />
                  {event.status}
                </span>
              </div>
              <p className="text-sm text-slate-700">{event.message}</p>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
