export function DashboardPage() {
  return (
    <section className="space-y-3">
      <h2 className="text-2xl font-semibold">Investigator Dashboard</h2>
      <p className="text-slate-300">Track evidence processing, timeline events, and unresolved evidence gaps.</p>
      <div className="rounded border border-slate-700 p-4">
        <p className="text-sm text-amber-300">Disclaimer: This MVP is decision-support only and never provides autonomous forensic verdicts.</p>
      </div>
    </section>
  );
}
