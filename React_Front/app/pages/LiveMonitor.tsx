import { Box, ShieldCheck, TriangleAlert } from "lucide-react";
import CameraFeed from "~/components/CameraFeed";
import LogsPanel from "~/components/LogsPanel";
import StatCard from "~/components/StatCard";
import StatusBadge from "~/components/StatusBadge";
import { DEFAULT_CAMERA_ID } from "~/lib/config";
import { useCameraMonitor } from "~/lib/useCameraMonitor";
import { detectionService } from "~/services/detection";

export function meta() {
  return [{ title: "Fine Graduation Project Dashboard" }];
}

export default function LiveMonitor() {
  const camId = DEFAULT_CAMERA_ID;
  const { stats, liveLogs, historyLogs, busy, error, toggle } =
    useCameraMonitor(camId);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <StatusBadge running={stats.is_running} />
        {error && <span className="text-xs text-amber-600">{error}</span>}
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <StatCard
          label="Total Tracked Packages"
          value={stats.total_tracked_packages}
          icon={Box}
          iconClass="text-blue-600"
        />
        <StatCard
          label="Defective Packages"
          value={stats.defective_packages}
          icon={TriangleAlert}
          iconClass="text-red-500"
          valueClass="text-3xl font-bold text-red-600"
        />
        <StatCard
          label="System Status"
          value={stats.system_status}
          icon={ShieldCheck}
          iconClass="text-emerald-500"
          valueClass={`text-xl font-semibold ${
            stats.is_running ? "text-emerald-600" : "text-orange-600"
          }`}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <CameraFeed
          camId={camId}
          feedUrl={detectionService.feedUrl(camId)}
          isRunning={stats.is_running}
          busy={busy}
          onToggle={toggle}
        />
        <LogsPanel liveLogs={liveLogs} historyLogs={historyLogs} />
      </div>
    </div>
  );
}