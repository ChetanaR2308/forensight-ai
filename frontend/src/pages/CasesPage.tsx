import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../hooks/useAuth";
import { useState } from "react";

export function CasesPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const casesQuery = useQuery({
    queryKey: ["cases"],
    queryFn: () => api.listCases(token!),
    enabled: Boolean(token),
  });

  const createCase = useMutation({
    mutationFn: () => api.createCase(token!, title, description),
    onSuccess: () => {
      setTitle("");
      setDescription("");
      queryClient.invalidateQueries({ queryKey: ["cases"] });
    },
  });

  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold">Cases</h2>
      <form
        className="grid gap-2 md:grid-cols-[1fr_2fr_auto]"
        onSubmit={(e) => {
          e.preventDefault();
          createCase.mutate();
        }}
      >
        <input className="rounded bg-slate-800 p-2" placeholder="Case title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input className="rounded bg-slate-800 p-2" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <button className="rounded bg-cyan-700 px-3">Create</button>
      </form>

      {casesQuery.isLoading && <p>Loading cases…</p>}
      {casesQuery.error && <p className="text-red-300">Failed to load cases</p>}
      {casesQuery.data?.length === 0 && <p className="text-slate-300">No cases yet.</p>}

      <ul className="space-y-2">
        {casesQuery.data?.map((item) => (
          <li key={item.id} className="rounded border border-slate-700 p-3">
            <Link className="text-cyan-300 hover:underline" to={`/cases/${item.id}`}>{item.title}</Link>
            <p className="text-sm text-slate-400">{item.description}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
