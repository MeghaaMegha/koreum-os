import { useEffect, useState } from "react";
import { api, User } from "../api/client";

const ROLES = ["ADMIN", "PLATFORM_ADMIN", "AI_ADMIN", "MANAGER", "USER", "AUDITOR"];

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role_names: ["USER"] });
  const [formError, setFormError] = useState("");
  const [creating, setCreating] = useState(false);

  const loadUsers = () => {
    setLoading(true);
    api
      .listUsers()
      .then((res) => setUsers(res.data))
      .catch((e) => setError(e.response?.data?.detail || "Failed to load users"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const toggleRole = (role: string) => {
    setForm((f) => ({
      ...f,
      role_names: f.role_names.includes(role)
        ? f.role_names.filter((r) => r !== role)
        : [...f.role_names, role],
    }));
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setCreating(true);
    api
      .createUser(form)
      .then(() => {
        setShowForm(false);
        setForm({ email: "", full_name: "", password: "", role_names: ["USER"] });
        loadUsers();
      })
      .catch((err) => setFormError(err.response?.data?.detail || "Failed to create user"))
      .finally(() => setCreating(false));
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800 mb-1">Users</h1>
          <p className="text-sm text-slate-500">User accounts in your tenant</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-koreum-500 text-white text-sm font-medium rounded-lg hover:bg-koreum-600 transition"
        >
          {showForm ? "Cancel" : "+ Create User"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Create New User</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Full Name</label>
              <input
                type="text"
                required
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-koreum-500"
                placeholder="Jane Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Email</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-koreum-500"
                placeholder="jane@example.com"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
              <input
                type="password"
                required
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-koreum-500"
                placeholder="Min 8 characters"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-600 mb-2">Roles</label>
              <div className="flex flex-wrap gap-2">
                {ROLES.map((role) => (
                  <button
                    key={role}
                    type="button"
                    onClick={() => toggleRole(role)}
                    className={`px-3 py-1 text-xs rounded-lg border transition ${
                      form.role_names.includes(role)
                        ? "bg-koreum-500 text-white border-koreum-500"
                        : "bg-white text-slate-600 border-slate-300 hover:border-koreum-300"
                    }`}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </div>
          </div>
          {formError && <p className="text-red-500 text-sm mt-3">{formError}</p>}
          <button
            type="submit"
            disabled={creating}
            className="mt-4 px-5 py-2 bg-koreum-500 text-white text-sm font-medium rounded-lg hover:bg-koreum-600 disabled:opacity-50 transition"
          >
            {creating ? "Creating..." : "Create User"}
          </button>
        </form>
      )}

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
                <td colSpan={4} className="px-5 py-8 text-center text-slate-400">Loading…</td>
              </tr>
            )}
            {error && (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-red-500">{error}</td>
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
                        <span key={r.id} className="text-[10px] px-2 py-0.5 rounded bg-koreum-50 text-koreum-700">
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
