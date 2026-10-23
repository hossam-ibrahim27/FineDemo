// import { useCallback, useEffect, useState } from "react";
// import type { CameraStats, InspectionLog } from "~/interfaces/detection";
// import { HISTORY_POLL_INTERVAL_MS, POLL_INTERVAL_MS } from "~/lib/config";
// import { detectionService } from "~/services/detection";

// const INITIAL_STATS: CameraStats = {
//   total_tracked_packages: 0,
//   defective_packages: 0,
//   system_status: "Standby Mode",
//   is_running: false,
// };

// export function useCameraMonitor(camId: string) {
//   const [stats, setStats] = useState<CameraStats>(INITIAL_STATS);
//   const [liveLogs, setLiveLogs] = useState<InspectionLog[]>([]);
//   const [historyLogs, setHistoryLogs] = useState<InspectionLog[]>([]);
//   const [busy, setBusy] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const refreshLive = useCallback(async () => {
//     try {
//       const [s, logs] = await Promise.all([
//         detectionService.getStats(camId),
//         detectionService.getLiveLogs(camId),
//       ]);
//       setStats(s);
//       setLiveLogs(logs);
//       setError(null);
//     } catch {
//       setError("Cannot reach the backend server.");
//     }
//   }, [camId]);

//   const refreshHistory = useCallback(async () => {
//     try {
//       setHistoryLogs(await detectionService.getHistoryLogs());
//     } catch {
//       /* الـ live polling بيعرض الخطأ */
//     }
//   }, []);

//   useEffect(() => {
//     refreshLive();
//     const id = setInterval(refreshLive, POLL_INTERVAL_MS);
//     return () => clearInterval(id);
//   }, [refreshLive]);

//   useEffect(() => {
//     refreshHistory();
//     const id = setInterval(refreshHistory, HISTORY_POLL_INTERVAL_MS);
//     return () => clearInterval(id);
//   }, [refreshHistory]);

//   const toggle = useCallback(async () => {
//     setBusy(true);
//     try {
//       if (stats.is_running) await detectionService.stop(camId);
//       else await detectionService.start(camId);
//       await refreshLive();
//     } catch {
//       setError("Action failed. Check the backend server.");
//     } finally {
//       setBusy(false);
//     }
//   }, [camId, stats.is_running, refreshLive]);

//   return { stats, liveLogs, historyLogs, busy, error, toggle };
// }





import { useCallback, useEffect, useState } from 'react'
import type { CameraStats, InspectionLog } from '~/interfaces/detection'
import { POLL_INTERVAL_MS } from '~/lib/config'
import { detectionService } from '~/services/detection'

const INITIAL_STATS: CameraStats = {
  total_tracked_packages: 0,
  defective_packages: 0,
  system_status: 'Standby Mode',
  is_running: false
}

interface UseCameraMonitorResult {
  stats: CameraStats
  liveLogs: InspectionLog[]
  historyLogs: InspectionLog[]
  busy: boolean
  error: string | null
  toggle: () => Promise<void>
}

export function useCameraMonitor(camId: string): UseCameraMonitorResult {
  const [stats, setStats] = useState<CameraStats>(INITIAL_STATS)
  const [liveLogs, setLiveLogs] = useState<InspectionLog[]>([])
  const [historyLogs, setHistoryLogs] = useState<InspectionLog[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshLive = useCallback(async (): Promise<void> => {
    try {
      const [s, logs] = await Promise.all([
        detectionService.getStats(camId),
        detectionService.getLiveLogs(camId)
      ])
      setStats(s)
      setLiveLogs(logs)
      setError(null)
    } catch {
      setError('Cannot reach the backend server.')
    }
  }, [camId])

  const refreshHistory = useCallback(async (): Promise<void> => {
    try {
      setHistoryLogs(await detectionService.getHistoryLogs())
    } catch {
      // the live polling already shows the error
    }
  }, [])

  useEffect(() => {
    const tick = (): void => {
      void refreshLive()
    }
    const first = setTimeout(tick, 0)
    const id = setInterval(tick, POLL_INTERVAL_MS)
    return () => {
      clearTimeout(first)
      clearInterval(id)
    }
  }, [refreshLive])

  // history: loaded once on open, then only after Stop
  useEffect(() => {
    const first = setTimeout(() => void refreshHistory(), 0)
    return () => clearTimeout(first)
  }, [refreshHistory])

  const toggle = useCallback(async (): Promise<void> => {
    setBusy(true)
    try {
      if (stats.is_running) {
        await detectionService.stop(camId)   // backend saves the session to MySQL here
        await refreshHistory()
      } else {
        await detectionService.start(camId)
      }
      await refreshLive()
    } catch {
      setError('Action failed. Check the backend server.')
    } finally {
      setBusy(false)
    }
  }, [camId, stats.is_running, refreshLive, refreshHistory])

  return { stats, liveLogs, historyLogs, busy, error, toggle }
}