import { useEffect, useState } from "react";
import { api, User } from "../api/client";

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listUsers()
      .then((res) => setUsers(res.data))
      .catch((e) =>
        setError(e.response?.data?.detail || "Failed to load users")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold text-slate-800 mb-1">Users</h1>
      <p className="text-sm text-slate-500 mb-6">
        User accounts in your tenant
      </p>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Name</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Email</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Roles</th>
              <th className="text-left px-5 py-3 font-medium text-slate-600">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-slate-400">
                  Loading…
                </td>
              </tr>
            )}
            {error && (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-red-500">
                  {error}
                </td>
              </tr>
            )}
            {!loading &&
              users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-5 py-3 text-slate-800">{u.full_name}</td>
                  <td className="px-5 py-3 text-slate-600">{u.email}</td>
                  <td className="px-5 py-3">
                    <div className="flex gap-1">
                      {u.roles.map((r) => (
                        <span
                          key={r.id}
                          className="text-[10px] px-2 py-0.5 rounded bg-koreum-50 text-koreum-700"
                        >
                          {r.name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    {u.is_active ? (
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
