import { Activity, Camera, House } from "lucide-react";
import { NavLink } from "react-router";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: House },
  { to: "/monitor", label: "Live Monitor", icon: Camera },
];

export default function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200 bg-white px-6 py-8 md:flex">
      <div>
        <div className="flex items-center gap-2">
          <Activity className="size-6 text-blue-600" />
          <span className="text-xl font-bold text-slate-900">InspectVision</span>
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Tissue &amp; Packaging Defect Monitor
        </p>

        <nav className="mt-8 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-600 hover:bg-slate-50"
                }`
              }
            >
              <Icon className="size-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="mt-auto border-t border-slate-200 pt-4">
        <p className="text-sm font-semibold text-slate-800">InspectVision Core</p>
        <p className="mt-1 text-xs text-slate-400">
          © 2026 Fine Graduation Project Team
        </p>
      </div>
    </aside>
  );
}