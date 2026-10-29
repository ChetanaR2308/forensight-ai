from __future__ import annotations

import { useMemo } from "react";

export function DashboardPage() {
  const summary = useMemo(
    () => [
      { label: "Cases", value: "0" },
      { label: "Evidence", value: "0" },
      { label: "Uncertainty", value: "0" },
      { label: "Conflicts", value: "0" },
    ],
    [],
  );

  return (
    <section className="space-y-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Investigator Dashboard</h2>
          <p className="text-slate-300">Track evidence processing, timeline events, and unresolved evidence gaps.</p>
        </div>
        <span className="rounded-full border border-amber-500/50 bg-amber-500/10 px-3 py-1 text-xs text-amber-300">
          Decision-support only
        </span>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        {summary.map((item) => (
          <div key={item.label} className="rounded border border-slate-700 bg-slate-900 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">{item.label}</div>
            <div className="mt-2 text-2xl font-semibold text-cyan-300">{item.value}</div>
          </div>
        ))}
      </div>

      <div className="rounded border border-slate-700 bg-slate-900 p-4">
        <h3 className="font-semibold">Forensic ethics</h3>
        <p className="mt-2 text-sm text-slate-300">
          This research prototype never infers guilt, identity, or innocence from a model result alone.
          Every finding must be grounded in source evidence and reviewed by a human investigator.
        </p>
      </div>

      <div className="rounded border border-slate-700 bg-slate-900 p-4">
        <h3 className="font-semibold">Current investigation workflow</h3>
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-300">
          <li>Upload CCTV, image, document, or witness evidence.</li>
          <li>Extract metadata, timestamps, and structured observations.</li>
          <li>Correlate events and examine evidence gaps and conflicts.</li>
          <li>Ask case-specific questions and review explainable reports.</li>
        </ul>
      </div>
    </section>
  );
}
