import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", icon: "▦" },
  { to: "/users", label: "Users", icon: "◯" },
  { to: "/tenants", label: "Tenants", icon: "▣" },
  { to: "/audit", label: "Audit Logs", icon: "≡" },
  { to: "/vault", label: "Vault", icon: "◈" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col">
        <div className="px-5 py-5 border-b border-slate-700">
          <div className="text-lg font-semibold tracking-tight">
            Koreum<span className="text-koreum-400"> OS</span>
          </div>
          <div className="text-xs text-slate-400 mt-0.5">
            Enterprise Agentic AI Platform
          </div>
        </div>
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-koreum-600 text-white"
                    : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-4 py-4 border-t border-slate-700">
          <div className="text-xs text-slate-400 mb-1">{user?.email}</div>
          <div className="flex flex-wrap gap-1 mb-3">
            {user?.roles.map((r) => (
              <span
                key={r}
                className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-300"
              >
                {r}
              </span>
            ))}
          </div>
          <button
            onClick={logout}
            className="w-full text-xs text-slate-400 hover:text-white border border-slate-700 rounded py-1.5 transition-colors hover:bg-slate-800"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
