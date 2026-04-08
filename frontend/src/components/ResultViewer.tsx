import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";

type ViewerTab = "report" | "json";

interface ResultViewerProps {
  result: unknown;
}

function hasMarkdownReport(value: unknown): value is { markdown_report: string } {
  if (!value || typeof value !== "object") return false;
  const candidate = value as { markdown_report?: unknown };
  return typeof candidate.markdown_report === "string";
}

function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function ResultViewer({ result }: ResultViewerProps) {
  const [activeTab, setActiveTab] = useState<ViewerTab>("report");

  const jsonText = useMemo(
    () => (result ? JSON.stringify(result, null, 2) : ""),
    [result]
  );
  const markdownText = useMemo(() => {
    if (!result) return "";
    if (typeof result === "string") return result;
    if (hasMarkdownReport(result)) return result.markdown_report;
    return "";
  }, [result]);

  const hasMarkdown = markdownText.trim().length > 0;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-slate-900">Result Viewer</h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("report")}
            disabled={!hasMarkdown}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activeTab === "report"
                ? "bg-sky-600 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            } disabled:cursor-not-allowed disabled:opacity-50`}
          >
            Report
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("json")}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activeTab === "json"
                ? "bg-sky-600 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            JSON
          </button>
        </div>
      </div>

      {!result ? (
        <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
          No final result yet. Run a scrape job to view output.
        </p>
      ) : (
        <>
          <div className="mb-3 flex items-center gap-2">
            {hasMarkdown && (
              <button
                type="button"
                onClick={() => downloadFile(markdownText, "scrape-report.md", "text/markdown")}
                className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
              >
                Download .md
              </button>
            )}
            <button
              type="button"
              onClick={() => downloadFile(jsonText, "scrape-result.json", "application/json")}
              className="rounded-md bg-slate-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800"
            >
              Download .json
            </button>
          </div>

          {activeTab === "report" && hasMarkdown ? (
            <article className="prose prose-slate max-w-none rounded-lg border border-slate-200 bg-slate-50 p-4">
              <ReactMarkdown>{markdownText}</ReactMarkdown>
            </article>
          ) : (
            <pre className="max-h-96 overflow-auto rounded-lg border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">
              {jsonText}
            </pre>
          )}
        </>
      )}
    </section>
  );
}
