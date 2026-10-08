import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Layout() {
  const { logout, role } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-700 p-4">
        <h1 className="text-xl font-bold">ForenSight AI — Research MVP</h1>
        <p className="text-sm text-amber-300">
          Human-in-the-loop software only. AI output is not proof of identity, guilt, or innocence.
        </p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-[240px_1fr]">
        <aside className="border-r border-slate-700 p-4 space-y-3">
          <Link className="block hover:text-cyan-300" to="/">Dashboard</Link>
          <Link className="block hover:text-cyan-300" to="/cases">Cases</Link>
          <button className="rounded bg-slate-800 px-3 py-1" onClick={logout}>Log out ({role})</button>
        </aside>
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
