export interface CameraStats {
  total_tracked_packages: number
  defective_packages: number
  system_status: string
  is_running: boolean
}

export interface InspectionLog {
  Camera: string
  'Track ID': number
  defective: 'defective' | 'good'
  Time: string
}

export interface ActionResponse {
  status: string
  message: string
}