export default function StatusBadge({ running }: { running: boolean }): React.JSX.Element{
  const styles = running
    ? 'border-emerald-200 bg-emerald-50 text-emerald-600'
    : 'border-red-200 bg-red-50 text-red-600'
  const dot = running ? 'bg-emerald-500' : 'bg-red-500'

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${styles}`}
    >
      <span className={`size-2 rounded-full ${dot}`} />
      {running ? 'SYSTEM ACTIVE' : 'SYSTEM PAUSED'}
    </span>
  )
}