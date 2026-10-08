import { createContext, useContext, useMemo, useState } from "react";
import { api } from "../api/client";

interface AuthContextValue {
  token: string | null;
  role: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [role, setRole] = useState<string | null>(localStorage.getItem("role"));

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      role,
      login: async (username: string, password: string) => {
        const data = await api.login(username, password);
        setToken(data.access_token);
        setRole(data.role);
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
      },
      logout: () => {
        setToken(null);
        setRole(null);
        localStorage.removeItem("token");
        localStorage.removeItem("role");
      },
    }),
    [role, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
