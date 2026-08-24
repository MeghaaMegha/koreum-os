import { useEffect, useState } from "react";
import { api, Tenant } from "../api/client";

export default function Tenants() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listTenants()
      .then((res) => setTenants(res.data))
      .catch((e) =>
        setError(e.response?.data?.detail || "Failed to load tenants")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-slate-800 mb-1">Tenants</h1>
      <p className="text-sm text-slate-500 mb-6">
        Organisations on the platform
      </p>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Name</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Slug</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Status</th>
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
              tenants.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 text-slate-800">{t.name}</td>
                  <td className="px-5 py-3 text-slate-500 font-mono text-xs">
                    {t.slug}
                  </td>
                  <td className="px-5 py-3">
                    {t.is_active ? (
                      <span className="text-xs text-emerald-600">● Active</span>
                    ) : (
                      <span className="text-xs text-slate-400">○ Inactive</span>
                    )}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
