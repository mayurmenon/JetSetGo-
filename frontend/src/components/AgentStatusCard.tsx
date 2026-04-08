import { CheckCircle2, Loader2, XCircle } from "lucide-react";

import type { AgentStatus } from "../types";

interface AgentStatusCardProps {
  events: AgentStatus[];
}

type AgentSummary = {
  agent_name: string;
  status: AgentStatus["status"];
  message: string;
};

function summarizeLatestByAgent(events: AgentStatus[]): AgentSummary[] {
  const map = new Map<string, AgentSummary>();
  events.forEach((event) => {
    map.set(event.agent_name, {
      agent_name: event.agent_name,
      status: event.status,
      message: event.message,
    });
  });
  return Array.from(map.values());
}

function statusStyles(status: AgentStatus["status"]) {
  if (status === "running") {
    return {
      icon: <Loader2 className="h-4 w-4 animate-spin text-sky-600" />,
      badge: "bg-sky-100 text-sky-700",
      card: "border-sky-200 bg-sky-50/40",
    };
  }
  if (status === "completed") {
    return {
      icon: <CheckCircle2 className="h-4 w-4 text-emerald-600" />,
      badge: "bg-emerald-100 text-emerald-700",
      card: "border-emerald-200 bg-emerald-50/40",
    };
  }
  return {
    icon: <XCircle className="h-4 w-4 text-rose-600" />,
    badge: "bg-rose-100 text-rose-700",
    card: "border-rose-200 bg-rose-50/40",
  };
}

export function AgentStatusCard({ events }: AgentStatusCardProps) {
  const agents = summarizeLatestByAgent(events);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 text-lg font-semibold text-slate-900">Agent Status</h2>
      {agents.length === 0 ? (
        <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
          No active agents yet.
        </p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => {
            const style = statusStyles(agent.status);
            return (
              <article
                key={agent.agent_name}
                className={`rounded-lg border p-3 ${style.card}`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-900">{agent.agent_name}</h3>
                  {style.icon}
                </div>
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ${style.badge}`}
                >
                  {agent.status}
                </span>
                <p className="mt-2 line-clamp-2 text-xs text-slate-600">{agent.message}</p>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
