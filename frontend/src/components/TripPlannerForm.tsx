import { type FormEvent, useMemo, useState } from "react";

import type { ScrapeRequest } from "../types";

type ScrapeStatus = "idle" | "submitting" | "running" | "completed" | "error";

interface TripPlannerFormProps {
  status: ScrapeStatus;
  startScrape: (request: ScrapeRequest) => Promise<void>;
}

const BUDGET_OPTIONS: ScrapeRequest["budget"][] = ["Budget", "Moderate", "Luxury"];

function todayIsoDate(): string {
  return new Date().toISOString().split("T")[0];
}

export function TripPlannerForm({ status, startScrape }: TripPlannerFormProps) {
  const [destination, setDestination] = useState("");
  const [originCity, setOriginCity] = useState("");
  const [startDate, setStartDate] = useState(todayIsoDate());
  const [endDate, setEndDate] = useState(todayIsoDate());
  const [budget, setBudget] = useState<ScrapeRequest["budget"]>("Moderate");

  const isBusy = status === "submitting" || status === "running";
  const endDateMin = useMemo(() => startDate || todayIsoDate(), [startDate]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const payload: ScrapeRequest = {
      destination: destination.trim(),
      origin_city: originCity.trim() || undefined,
      start_date: startDate,
      end_date: endDate,
      budget,
    };
    await startScrape(payload);
  };

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
    >
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-1">
          <label htmlFor="destination" className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Destination
          </label>
          <input
            id="destination"
            type="text"
            required
            disabled={isBusy}
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="Tokyo"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="origin-city" className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Origin City (Optional)
          </label>
          <input
            id="origin-city"
            type="text"
            disabled={isBusy}
            value={originCity}
            onChange={(e) => setOriginCity(e.target.value)}
            placeholder="Hong Kong"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="start-date" className="text-sm font-medium text-slate-700 dark:text-slate-200">
            Start Date
          </label>
          <input
            id="start-date"
            type="date"
            required
            disabled={isBusy}
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="end-date" className="text-sm font-medium text-slate-700 dark:text-slate-200">
            End Date
          </label>
          <input
            id="end-date"
            type="date"
            required
            min={endDateMin}
            disabled={isBusy}
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
          />
        </div>
      </div>

      <div className="space-y-1">
        <label htmlFor="budget" className="text-sm font-medium text-slate-700 dark:text-slate-200">
          Budget
        </label>
        <select
          id="budget"
          disabled={isBusy}
          value={budget}
          onChange={(e) => setBudget(e.target.value as ScrapeRequest["budget"])}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
        >
          {BUDGET_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={isBusy}
        className="inline-flex items-center rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
      >
        {isBusy ? "Planning Trip..." : "Generate Trip Plan"}
      </button>
    </form>
  );
}
