import type { Dispatch, SetStateAction } from "react";
import type { Log } from "~/interfaces/interfaces";

interface DatabaseTableViewProps {
  liveLogs: Log[];
  historyLogs: Log[];
  activeTab: "live" | "history";
  setActiveTab: Dispatch<SetStateAction<"live" | "history">>;
}

const DatabaseTableView = ({
  liveLogs,
  historyLogs,
  activeTab,
  setActiveTab,
}: DatabaseTableViewProps) => {
  const currentLogs = activeTab === "live" ? liveLogs : historyLogs;

  const getLogData = (log: Log) => {
    const rawDamage = log.damage ?? log.damage_status ?? "Normal";
    let damageText = "Normal";

    if (typeof rawDamage === "boolean") {
      damageText = rawDamage ? "Damaged" : "Normal";
    } else if (typeof rawDamage === "string") {
      damageText = rawDamage.toLowerCase().includes("damage") || rawDamage.toLowerCase() === "yes" 
        ? "Damaged" 
        : "Normal";
    }

    return {
      camera: log.Camera || log.camera_id || "CAM #1",
      trackId: log["Track ID"] ?? log.track_id ?? "N/A",
      damage: damageText,
      time: log.Time || log.timestamp_str || log.created_at || new Date().toLocaleTimeString(),
    };
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex flex-col">
      <h3 className="text-xs font-bold text-slate-700 tracking-wider mb-4 uppercase">
        • Database INSPECTION LOGS
      </h3>
      
      {/* Tabs */}
      <div className="flex border-b border-slate-200 mb-4">
        <button
          className={`pb-2 px-4 font-medium transition-colors ${
            activeTab === "live"
              ? "border-b-2 border-blue-600 text-blue-600 font-semibold"
              : "text-slate-400 hover:text-slate-600"
          }`}
          onClick={() => setActiveTab("live")}
        >
          Live Session ({liveLogs.length})
        </button>
        <button
          className={`pb-2 px-4 font-medium transition-colors ${
            activeTab === "history"
              ? "border-b-2 border-blue-600 text-blue-600 font-semibold"
              : "text-slate-400 hover:text-slate-600"
          }`}
          onClick={() => setActiveTab("history")}
        >
          Database History ({historyLogs.length})
        </button>
      </div>

      {/* Table Container */}
      <div className="overflow-y-auto max-h-85 flex-1">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100 sticky top-0 text-slate-700 font-semibold border-b border-slate-200">
            <tr>
              <th className="py-2.5 px-3">Camera</th>
              <th className="py-2.5 px-3">Track ID</th>
              <th className="py-2.5 px-3">Status / Defect</th>
              <th className="py-2.5 px-3">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {currentLogs.map((logItem, index) => {
              const { camera, trackId, damage, time } = getLogData(logItem);
              const isDamaged = damage === "Damaged";

              return (
                <tr key={`${trackId}-${index}`} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-slate-700 uppercase">
                    {camera}
                  </td>
                  <td className="py-3 px-3 text-slate-500 font-mono">
                    #{trackId}
                  </td>

                  {/* Damage Status Badge */}
                  <td className="py-3 px-3">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded text-xs font-semibold ${
                        isDamaged
                          ? "bg-rose-50 text-rose-600 border border-rose-200"
                          : "bg-emerald-50 text-emerald-600 border border-emerald-200"
                      }`}
                    >
                      {damage}
                    </span>
                  </td>

                  <td className="py-3 px-3 text-slate-400 text-[11px] font-mono">
                    {time}
                  </td>
                </tr>
              );
            })}

            {currentLogs.length === 0 && (
              <tr>
                <td colSpan={4} className="text-center py-8 text-slate-400">
                  No logs found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DatabaseTableView;