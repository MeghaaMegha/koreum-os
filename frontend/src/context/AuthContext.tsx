import React, { createContext, useContext, useEffect, useState } from "react";
import { api, MeResponse } from "../api/client";

interface AuthState {
  token: string | null;
  user: MeResponse | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("koreum_access_token")
  );
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("koreum_access_token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await api.login(email, password);
    const { access_token, refresh_token } = res.data;
    localStorage.setItem("koreum_access_token", access_token);
    localStorage.setItem("koreum_refresh_token", refresh_token);
    setToken(access_token);
    const me = await api.me();
    setUser(me.data);
  };

  const logout = () => {
    localStorage.removeItem("koreum_access_token");
    localStorage.removeItem("koreum_refresh_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
