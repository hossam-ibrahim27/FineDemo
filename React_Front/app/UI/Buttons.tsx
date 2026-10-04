import { Play, Square } from "lucide-react";
interface RefreshButtonProps {
  isMonitoring: boolean; 
  cameraId?: string;
  fetchHistoryLogs?: () => void;
  handleStart?: (camId?: string) => void;
  handleStop?: (camId?: string) => void;
  disabled?: boolean; 
}

const Buttons = ({ 
  handleStart, 
  handleStop, 
  isMonitoring, 
  cameraId,
  disabled = false 
}: RefreshButtonProps) => {
  return (
    <div className="flex gap-3">
      {!isMonitoring ? (
        <button
          disabled={disabled}
          onClick={() => handleStart?.(cameraId)}
          className="flex items-center cursor-pointer gap-2 text-xs font-semibold px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white rounded-lg shadow-sm transition-all active:scale-95"
        >
          <Play className="w-3.5 h-3.5 text-emerald-100 fill-current" />
          Start
        </button>
      ) : (
        <button
          disabled={disabled}
          onClick={() => handleStop?.(cameraId)}
          className="flex items-center cursor-pointer gap-2 text-xs font-semibold px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:bg-slate-300 text-white rounded-lg shadow-sm transition-all active:scale-95"
        >
          <Square className="w-3.5 h-3.5 text-rose-100 fill-current" />
          Stop & Save
        </button>
      )}
    </div>
  );
};

export default Buttons;