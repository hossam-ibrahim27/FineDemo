import { Camera, Monitor, Play, Square } from 'lucide-react'
import { useState } from 'react'

interface Props {
  camId: string
  feedUrl: string
  isRunning: boolean
  busy: boolean
  onToggle: () => void
}

export default function CameraFeed({ camId, feedUrl, isRunning, busy, onToggle }: Props): React.JSX.Element {
  const [feedFailed, setFeedFailed] = useState(false)

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="flex items-center gap-2 font-semibold uppercase text-slate-800">
          <Camera className="size-5 text-blue-600" />
          Live Camera Feed
        </h2>
        <span className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-blue-600 shadow-sm">
          <Monitor className="size-3.5" />
          CAM #{camId}
        </span>
      </div>

      <div className="rounded-xl border border-slate-200 p-5">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-slate-700">
            <span className="size-1.5 rounded-full bg-slate-700" />
            Live Camera Feed Camera#{camId}
          </h3>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-bold ${
              feedFailed
                ? 'border-slate-200 bg-slate-50 text-slate-500'
                : 'border-emerald-200 bg-emerald-50 text-emerald-600'
            }`}
          >
            <span
              className={`size-1.5 rounded-full ${feedFailed ? 'bg-slate-400' : 'bg-emerald-500'}`}
            />
            {feedFailed ? 'OFFLINE' : 'LIVE'}
          </span>
        </div>

        <div className="relative aspect-[1020/500] overflow-hidden rounded-lg bg-[#020617]">
          <img
            src={feedUrl}
            alt={`Conveyor Line Feed ${camId}`}
            onLoad={() => setFeedFailed(false)}
            onError={() => setFeedFailed(true)}
            className="h-full w-full object-cover"
          />
          {feedFailed && (
            <div className="absolute inset-0 flex items-center justify-center text-sm text-slate-400">
              Camera feed unavailable
            </div>
          )}
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <p className="text-xs text-slate-500">Tissue Production Line</p>
        <button
          onClick={onToggle}
          disabled={busy}
          className={`inline-flex cursor-pointer items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors disabled:opacity-60 ${
            isRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-emerald-600 hover:bg-emerald-700'
          }`}
        >
          {isRunning ? (
            <Square className="size-4 fill-current" />
          ) : (
            <Play className="size-4 fill-current" />
          )}
          {isRunning ? 'Stop' : 'Start'}
        </button>
      </div>
    </section>
  )
}