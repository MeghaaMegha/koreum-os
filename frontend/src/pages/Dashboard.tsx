import { useEffect, useState } from "react";
import { api } from "../api/client";

interface DashboardStats {
  total_users: number;
  audit_events: number;
  total_tenants: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_users: 0,
    audit_events: 0,
    total_tenants: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [usersRes, auditRes, tenantsRes] = await Promise.all([
          api.listUsers(),
          api.listAudit(),
          api.listTenants(),
        ]);
        setStats({
          total_users: usersRes.data.length,
          audit_events: auditRes.data.items.length,
          total_tenants: tenantsRes.data.length,
        });
      } catch (err) {
        console.error("Failed to load stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const cards = [
    { label: "TOTAL USERS", value: stats.total_users },
    { label: "AUDIT EVENTS", value: stats.audit_events },
    { label: "TENANTS", value: stats.total_tenants },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">
          Welcome back, Koreum Admin. Here's the platform overview.
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {cards.map((card) => (
          <div
            key={card.label}
            className="bg-white rounded-lg border border-slate-200 p-5 shadow-sm"
          >
            <div className="text-xs font-medium text-slate-500 tracking-wide">
              {card.label}
            </div>
            <div className="text-3xl font-bold text-slate-800 mt-2">
              {loading ? "—" : card.value}
            </div>
          </div>
        ))}
      </div>

      {/* Platform Status */}
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
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="text-slate-600">
              Phase 2 — Koreum Vault: Active
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
