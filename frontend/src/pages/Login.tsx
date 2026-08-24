import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@koreum.local");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || "Login failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-white">
            Koreum<span className="text-koreum-400"> OS</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Enterprise Agentic AI Operating Platform
          </p>
        </div>
        <form
          onSubmit={handleSubmit}
          className="bg-slate-800 rounded-lg p-6 shadow-xl space-y-4"
        >
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-900 text-white rounded-md px-3 py-2 text-sm border border-slate-700 focus:border-koreum-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-900 text-white rounded-md px-3 py-2 text-sm border border-slate-700 focus:border-koreum-500 focus:outline-none"
              required
            />
          </div>
          {error && (
            <div className="text-xs text-red-400 bg-red-950/50 rounded px-3 py-2">
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-koreum-600 hover:bg-koreum-700 text-white text-sm font-medium rounded-md py-2.5 transition-colors disabled:opacity-50"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="text-center text-xs text-slate-500 mt-4">
          Seeded admin: admin@koreum.local / Admin123!
        </p>
      </div>
    </div>
  );
}
