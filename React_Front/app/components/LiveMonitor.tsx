import React, { useState } from "react";
import { Camera as CameraIcon, LayoutGrid, Monitor } from "lucide-react"; 
import Camera from "~/components/Camera"; 
import Buttons from "~/UI/Buttons";

interface VideoMonitorProps {
  isMonitoring: boolean;
  fetchHistoryLogs?: () => void;
  handleStart?: (camId?: string) => void;
  handleStop?: (camId?: string) => void;
}

const CAMERAS = [
  { id: "1", number: 1, name: "Tissue Production Line" },
];

export const LiveMonitor: React.FC<VideoMonitorProps> = React.memo(({ isMonitoring, handleStart, handleStop }) => {
  const [selectedCamNumber, setSelectedCamNumber] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"single" | "grid">("single");

  const getStreamUrl = (camNumber: number) => {
    return `http://localhost:8000/api/v1/${camNumber}/feed?t=${isMonitoring ? "active" : "standby"}`;
  };

  const selectedCamera = CAMERAS.find((cam) => cam.number === selectedCamNumber) || CAMERAS[0];

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div className="flex items-center gap-2">
          <CameraIcon className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-slate-800 text-sm tracking-wide uppercase flex items-center gap-2">
            Live Camera Feed
            {isMonitoring && (
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
            )}
          </h2>
        </div>

        {/* View Mode & Camera Selectors */}
        <div className="flex items-center gap-2">
          {CAMERAS.length > 1 && (
            <button
              onClick={() => setViewMode(viewMode === "single" ? "grid" : "single")}
              className={`p-1.5 rounded-lg border text-xs font-medium transition-all ${
                viewMode === "grid"
                  ? "bg-blue-50 border-blue-200 text-blue-600"
                  : "border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
              title="Toggle Grid / Single View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          )}

          <div className="flex bg-slate-100 p-1 rounded-lg text-xs font-medium text-slate-600">
            {CAMERAS.map((cam) => (
              <button
                key={cam.id}
                onClick={() => {
                  setSelectedCamNumber(cam.number);
                  setViewMode("single");
                }}
                className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
                  viewMode === "single" && selectedCamNumber === cam.number
                    ? "bg-white text-blue-600 shadow-sm font-semibold"
                    : "hover:text-slate-900"
                }`}
              >
                <Monitor className="w-3.5 h-3.5" />
                CAM #{cam.number}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Stream Display Area */}
      {viewMode === "single" ? (
        <div className="max-w-4xl mx-auto w-full space-y-3">
          <Camera 
            cameraNumber={selectedCamera.number}
            src={getStreamUrl(selectedCamera.number)}
            alt={`Conveyor Line Feed ${selectedCamera.number}`}
          />
          <div className="flex justify-between items-center pt-1">
            <span className="text-xs font-medium text-slate-500">
              {selectedCamera.name}
            </span>
            <Buttons
              isMonitoring={isMonitoring} 
              cameraId={selectedCamera.id} 
              handleStart={() => handleStart && handleStart(selectedCamera.id)} 
              handleStop={() => handleStop && handleStop(selectedCamera.id)}
            />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {CAMERAS.map((cam) => (
            <div key={cam.id} className="flex flex-col gap-2 bg-slate-50 p-2 rounded-lg border border-slate-100">
              <Camera 
                cameraNumber={cam.number} 
                src={getStreamUrl(cam.number)}
                alt={`Conveyor Line Feed ${cam.name}`}
              />
              <div className="flex justify-between items-center">
                <span className="text-xs font-medium text-slate-500">{cam.name}</span>
                <Buttons
                  isMonitoring={isMonitoring} 
                  cameraId={cam.id}
                  handleStart={() => handleStart && handleStart(cam.id)} 
                  handleStop={() => handleStop && handleStop(cam.id)}
                />
              </div>
            </div>  
          ))}
        </div>
      )}
    </div>
  );
});

export default LiveMonitor;