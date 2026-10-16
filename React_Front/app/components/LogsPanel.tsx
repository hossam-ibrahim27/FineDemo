import { useState } from "react";
import type { InspectionLog } from "~/interfaces/detection";

type Tab = "live" | "history";

interface Props {
  liveLogs: InspectionLog[];
  historyLogs: InspectionLog[];
}

export default function LogsPanel({ liveLogs, historyLogs }: Props) {
  const [tab, setTab] = useState<Tab>("live");
  const logs = tab === "live" ? liveLogs : historyLogs;

  const tabs: { key: Tab; label: string }[] = [
    { key: "live", label: `Live Session (${liveLogs.length})` },
    { key: "history", label: `Database History (${historyLogs.length})` },
  ];

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-slate-700">
        <span className="size-1.5 rounded-full bg-slate-700" />
        Database Inspection Logs
      </h2>

      <div className="mt-4 flex gap-6 border-b border-slate-200">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`-mb-px border-b-2 px-1 pb-3 text-base font-medium transition-colors ${
              tab === key
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-400 hover:text-slate-600"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="mt-4 max-h-[480px] overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-slate-100 text-slate-700">
            <tr>
              <th className="px-3 py-3 font-semibold">Camera</th>
              <th className="px-3 py-3 font-semibold">Track ID</th>
              <th className="px-3 py-3 font-semibold">Status / Defect</th>
              <th className="px-3 py-3 text-right font-semibold">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, i) => (
              <tr
                key={`${log["Track ID"]}-${log.Time}-${i}`}
                className="border-b border-slate-100"
              >
                <td className="px-3 py-3 text-slate-700">{log.Camera}</td>
                <td className="px-3 py-3 text-slate-700">{log["Track ID"]}</td>
                <td className="px-3 py-3">
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                      log.damage === "Damaged"
                        ? "bg-red-50 text-red-600"
                        : "bg-emerald-50 text-emerald-600"
                    }`}
                  >
                    {log.damage}
                  </span>
                </td>
                <td className="px-3 py-3 text-right text-slate-500">{log.Time}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {logs.length === 0 && (
          <p className="py-10 text-center text-sm text-slate-400">No logs found.</p>
        )}
      </div>
    </section>
  );
}