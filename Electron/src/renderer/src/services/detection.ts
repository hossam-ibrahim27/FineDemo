import { API_BASE_URL } from '~/lib/config'
import type { ActionResponse, CameraStats, InspectionLog } from '~/interfaces/detection'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, init)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const detectionService = {
  feedUrl: (camId: string) => `${API_BASE_URL}/api/v1/${camId}/feed`,

  start: (camId: string) => request<ActionResponse>(`/api/v1/${camId}/start`, { method: 'POST' }),

  stop: (camId: string) => request<ActionResponse>(`/api/v1/${camId}/stop`, { method: 'POST' }),

  getStats: (camId: string) => request<CameraStats>(`/api/v1/${camId}/stats`),

  getLiveLogs: (camId: string) => request<InspectionLog[]>(`/api/v1/${camId}/live_session_logs`),

  getHistoryLogs: () => request<InspectionLog[]>('/api/history_logs')
}