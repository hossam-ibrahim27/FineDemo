import { useState, useEffect } from "react";
import { VideoOff, RotateCcw } from "lucide-react";

interface CameraProps {
  cameraNumber: number;
  src: string;
  alt: string;
  className?: string;
}

const Camera = ({ cameraNumber, src, alt, className = "" }: CameraProps) => {
  const [hasError, setHasError] = useState(false);
  const [retryKey, setRetryKey] = useState(Date.now());

  useEffect(() => {
    setHasError(false);
  }, [src]);

  const handleRetry = () => {
    setHasError(false);
    setRetryKey(Date.now()); 
  };

  const streamSrc = `${src}${src.includes("?") ? "&" : "?"}_retry=${retryKey}`;

  return (
    <div className={`bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold text-slate-700 tracking-wider uppercase">
          • Live Camera Feed Camera#{cameraNumber}
        </h3>
        
        {!hasError ? (
          <span className="flex items-center gap-1.5 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            LIVE
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
            OFFLINE
          </span>
        )}
      </div>

      {/* Video Display Container */}
      <div className="relative rounded-lg overflow-hidden bg-slate-950 w-full h-72 sm:h-80 flex items-center justify-center">
        {!hasError ? (
          <img
            key={retryKey}
            src={streamSrc}
            alt={alt}
            onError={() => setHasError(true)}
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 text-slate-400 p-4 text-center">
            <VideoOff className="w-8 h-8 text-rose-500/80 mb-1" />
            <div>
              <p className="text-xs font-medium text-slate-300">Camera Feed Unavailable</p>
              <span className="text-[11px] text-slate-500 block mt-0.5">
                Check signal or stream connection
              </span>
            </div>
            
            {/* Retry Button */}
            <button
              onClick={handleRetry}
              className="mt-1 flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-md transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reconnect
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Camera;