import { Activity } from "lucide-react";
import { Link } from "react-router";

const LINKS = [
  { href: "#features", label: "Features" },
  { href: "#how", label: "How it works" },
  { href: "#tech", label: "Tech stack" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <Activity className="size-6 text-blue-600" />
          <span className="text-lg font-bold text-slate-900">InspectVision</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-sm font-medium text-slate-600 transition-colors hover:text-blue-600"
            >
              {l.label}
            </a>
          ))}
        </nav>

        <Link
          to="/monitor"
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700"
        >
          Live Monitor
        </Link>
      </div>
    </header>
  );
}