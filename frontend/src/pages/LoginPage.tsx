import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("investigator");
  const [password, setPassword] = useState("investigator123");
  const [error, setError] = useState("");

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="mx-auto mt-20 max-w-md rounded border border-slate-700 bg-slate-900 p-6">
      <h2 className="text-2xl font-semibold">Sign in</h2>
      <p className="text-sm text-slate-300">Use documented local demo credentials.</p>
      <form onSubmit={onSubmit} className="space-y-3 mt-4">
        <input className="w-full rounded bg-slate-800 p-2" aria-label="username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input className="w-full rounded bg-slate-800 p-2" aria-label="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        {error && <p className="text-red-300">{error}</p>}
        <button className="w-full rounded bg-cyan-700 p-2">Login</button>
      </form>
    </div>
  );
}
