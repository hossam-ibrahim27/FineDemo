import { useEffect, useState } from "react";
import type { Log } from "~/interfaces/interfaces";
import DashboardCards from "./DashboardCards";
import { AlertTriangle, Box, ShieldCheck } from "lucide-react";
import DatabaseTableView from "./DatabaseTableView";
import LiveMonitor from "./LiveMonitor";

const CAMERAS_LIST = ["1"];

const Main = () => {
  // ********************************* States ****************************************
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [activeTab, setActiveTab] = useState<"live" | "history">("live");
  const [liveLogs, setLiveLogs] = useState<Log[]>([]);
  const [historyLogs, setHistoryLogs] = useState<Log[]>([]);
  const [stats, setStats] = useState({
    total_tracked_packages: 0,
    defective_packages: 0,
  });

  // ********************************** Actions *****************************************
  const fetchHistoryLogs = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/history_logs");
      if (res.ok) {
        const data = await res.json();
        setHistoryLogs(data);
      }
    } catch (err) {
      console.error("Failed to fetch history logs", err);
    }
  };

  useEffect(() => {
    fetchHistoryLogs();
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        let aggregatedPackages = 0;
        let aggregatedDefects = 0;
        let anyActive = false;

        const statsPromises = CAMERAS_LIST.map((camId) =>
          fetch(`http://localhost:8000/api/v1/${camId}/stats`).then((res) =>
            res.ok ? res.json() : null
          )
        );
        const statsResults = await Promise.all(statsPromises);

        statsResults.forEach((statsData) => {
          if (statsData) {
            aggregatedPackages += statsData.total_tracked_packages || 0;
            aggregatedDefects += statsData.defective_packages || 0;
            if (statsData.is_running) anyActive = true;
          }
        });

        setStats({
          total_tracked_packages: aggregatedPackages,
          defective_packages: aggregatedDefects,
        });
        setIsMonitoring(anyActive);

        if (anyActive) {
          const livePromises = CAMERAS_LIST.map((camId) =>
            fetch(`http://localhost:8000/api/v1/${camId}/live_session_logs`).then(
              (res) => (res.ok ? res.json() : [])
            )
          );
          const liveResults = await Promise.all(livePromises);
          const aggregatedLiveLogs = liveResults.flat();
          setLiveLogs(aggregatedLiveLogs);
        }
      } catch (err) {
        console.error("Error polling camera data", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleStart = async (camId?: string) => {
    try {
      const targetCams = camId ? [camId] : CAMERAS_LIST;
      await Promise.all(
        targetCams.map((id) =>
          fetch(`http://localhost:8000/api/v1/${id}/start`, { method: "POST" })
        )
      );
      setIsMonitoring(true);
      setActiveTab("live");
    } catch (err) {
      console.error("Error starting camera streams", err);
    }
  };

  const handleStop = async (camId?: string) => {
    try {
      const targetCams = camId ? [camId] : CAMERAS_LIST;
      await Promise.all(
        targetCams.map((id) =>
          fetch(`http://localhost:8000/api/v1/${id}/stop`, { method: "POST" })
        )
      );
      setIsMonitoring(false);
      fetchHistoryLogs();
    } catch (err) {
      console.error("Error stopping camera streams", err);
    }
  };

  // ***************************************************************************
  return (
    <section className="flex-1 p-6 lg:p-8 overflow-y-auto">
      {/* Header Bar */}
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div
          className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full border ${
            isMonitoring
              ? "text-emerald-600 bg-emerald-50 border-emerald-200"
              : "text-rose-600 bg-rose-50 border-rose-200"
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isMonitoring ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
            }`}
          ></span>
          {isMonitoring ? "SYSTEM MONITORING ACTIVE" : "SYSTEM PAUSED"}
        </div>
      </header>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
        <DashboardCards
          title="Total Tracked Packages"
          count={
            <h2 className="text-3xl font-bold text-slate-900 mt-2">
              {stats.total_tracked_packages}
            </h2>
          }
          component={<Box className="w-5 h-5 text-blue-500" />}
        />
        <DashboardCards
          title="Defective Packages"
          count={
            <h2 className="text-3xl font-bold text-red-500 mt-2">
              {stats.defective_packages}
            </h2>
          }
          component={<AlertTriangle className="w-5 h-5 text-red-500" />}
        />
        <DashboardCards
          title="System Status"
          count={
            <h3
              className={`text-base font-semibold mt-4 ${
                isMonitoring ? "text-emerald-600" : "text-amber-600"
              }`}
            >
              {isMonitoring ? "Active Surveillance" : "Standby Mode"}
            </h3>
          }
          component={<ShieldCheck className="w-5 h-5 text-emerald-500" />}
        />
      </div>

      {/* Live Stream & Table Container */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Live Video View */}
        <LiveMonitor
          isMonitoring={isMonitoring}
          handleStart={handleStart}
          handleStop={handleStop}
          fetchHistoryLogs={fetchHistoryLogs}
        />

        {/* Database Table View */}
        <DatabaseTableView
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          historyLogs={historyLogs}
          liveLogs={liveLogs}
        />
      </div>
    </section>
  );
};

export default Main;