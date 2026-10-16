import { Activity } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 py-8 sm:flex-row">
        <div className="flex items-center gap-2">
          <Activity className="size-5 text-blue-600" />
          <span className="text-sm font-semibold text-slate-800">InspectVision Core</span>
        </div>
        <p className="text-xs text-slate-400">© 2026 Fine Graduation Project Team</p>
      </div>
    </footer>
  );
}