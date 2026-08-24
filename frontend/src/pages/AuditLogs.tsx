import { useEffect, useState } from "react";
import { api, AuditEvent } from "../api/client";

export default function AuditLogs() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listAudit()
      .then((res) => setEvents(res.data.items))
      .catch((e) =>
        setError(e.response?.data?.detail || "Failed to load audit logs")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-slate-800 mb-1">Audit Logs</h1>
      <p className="text-sm text-slate-500 mb-6">
        Significant platform events (tenant-scoped)
      </p>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-5 py-3 font-medium text-slate-600">
                Action
              </th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">
                Details
              </th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">
                Timestamp
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={3} className="px-5 py-8 text-center text-slate-400">
                  Loading…
                </td>
              </tr>
            )}
            {error && (
              <tr>
                <td colSpan={3} className="px-5 py-8 text-center text-red-500">
                  {error}
                </td>
              </tr>
            )}
            {!loading &&
              events.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3">
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {ev.action}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-500 font-mono text-xs">
                    {ev.details ? JSON.stringify(ev.details) : "—"}
                  </td>
                  <td className="px-5 py-3 text-slate-500 text-xs">
                    {new Date(ev.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
