import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export function CaseDetailPage() {
  const { token } = useAuth();
  const { caseId = "" } = useParams();
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState("Summarize observed facts");
  const [assistant, setAssistant] = useState<string>("");
  const [reportSummary, setReportSummary] = useState("");

  const evidenceQuery = useQuery({
    queryKey: ["evidence", caseId],
    queryFn: () => api.listEvidence(token!, caseId),
    enabled: Boolean(token && caseId),
  });

  const timelineQuery = useQuery({
    queryKey: ["timeline", caseId],
    queryFn: () => api.getTimeline(token!, caseId),
    enabled: Boolean(token && caseId),
  });

  const upload = useMutation({
    mutationFn: (file: File) => api.uploadEvidence(token!, caseId, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["evidence", caseId] }),
  });

  const onUpload = (event: FormEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    if (file) upload.mutate(file);
  };

  const ask = async () => {
    const response = await api.queryCase(token!, caseId, question);
    const citations = response.result.citations.map((item) => item.evidence_id).join(", ") || "none";
    setAssistant(`${response.result.answer} | Status: ${response.result.status} | Citations: ${citations}`);
  };

  const generateReport = async () => {
    const response = await api.getReport(token!, caseId);
    setReportSummary(response.report.summary);
  };

  return (
    <section className="space-y-6">
      <h2 className="text-2xl font-semibold">Case detail</h2>

      <div className="rounded border border-slate-700 p-4">
        <h3 className="font-semibold">Evidence upload</h3>
        <input aria-label="upload evidence" type="file" onChange={onUpload} />
      </div>

      <div className="rounded border border-slate-700 p-4 overflow-auto">
        <h3 className="font-semibold">Evidence status / hash</h3>
        <table className="w-full text-sm">
          <thead><tr><th>File</th><th>Status</th><th>SHA-256</th></tr></thead>
          <tbody>
            {evidenceQuery.data?.map((item) => (
              <tr key={item.id}><td>{item.filename}</td><td>{item.processing_status}</td><td className="break-all">{item.sha256}</td></tr>
            ))}
          </tbody>
        </table>
        {evidenceQuery.data?.length === 0 && <p className="text-slate-400">No evidence uploaded yet.</p>}
      </div>

      <div className="rounded border border-slate-700 p-4">
        <h3 className="font-semibold">Timeline</h3>
        <ul className="space-y-2">
          {timelineQuery.data?.events.map((event) => (
            <li key={event.id} className="rounded bg-slate-900 p-2">
              <span className="text-cyan-300">{new Date(event.timestamp).toLocaleString()}</span> — {event.description} ({event.status})
            </li>
          ))}
        </ul>
      </div>

      <div className="rounded border border-slate-700 p-4 space-y-2">
        <h3 className="font-semibold">Investigation assistant</h3>
        <p className="text-xs text-amber-300">The assistant must not infer guilt or identity without supporting evidence.</p>
        <input className="w-full rounded bg-slate-800 p-2" value={question} onChange={(e) => setQuestion(e.target.value)} />
        <button className="rounded bg-cyan-700 px-3 py-1" onClick={ask}>Ask</button>
        {assistant && <p className="text-sm text-slate-200">{assistant}</p>}
      </div>

      <div className="rounded border border-slate-700 p-4 space-y-2">
        <h3 className="font-semibold">Report view / evidence gaps</h3>
        <button className="rounded bg-cyan-700 px-3 py-1" onClick={generateReport}>Generate report</button>
        {reportSummary && <p>{reportSummary}</p>}
      </div>
    </section>
  );
}
