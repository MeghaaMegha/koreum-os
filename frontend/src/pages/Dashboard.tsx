import { useEffect, useState } from "react";
import { api, MeResponse } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface Stats {
  totalUsers: number;
  totalAuditEvents: number;
  totalTenants: number;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({
    totalUsers: 0,
    totalAuditEvents: 0,
    totalTenants: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.listUsers().catch(() => ({ data: [] })),
      api.listAudit().catch(() => ({ data: { items: [], total: 0 } })),
      api.listTenants().catch(() => ({ data: [] })),
    ])
      .then(([usersRes, auditRes, tenantsRes]) => {
        setStats({
          totalUsers: (usersRes.data as unknown[]).length,
          totalAuditEvents: (auditRes.data as { total: number }).total,
          totalTenants: (tenantsRes.data as unknown[]).length,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const cards = [
    { label: "Total Users", value: stats.totalUsers, accent: "text-koreum-600" },
    { label: "Audit Events", value: stats.totalAuditEvents, accent: "text-emerald-600" },
    { label: "Tenants", value: stats.totalTenants, accent: "text-amber-600" },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Welcome back, {user?.full_name}. Here's the platform overview.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
        {cards.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-lg border border-slate-200 p-5 shadow-sm"
          >
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">
              {card.label}
            </div>
            <div className={`text-3xl font-semibold mt-2 ${card.accent}`}>
              {loading ? "…" : card.value}
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">
          Platform Status
        </h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-slate-600">Phase 1 — Foundation: Active</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-300"></span>
            <span className="text-slate-400">
              Phase 2 — Koreum Vault: Pending
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-300"></span>
            <span className="text-slate-400">
              Phase 4 — Koreum Fabric: Pending
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
