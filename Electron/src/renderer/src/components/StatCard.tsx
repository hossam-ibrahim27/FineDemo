import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface Props {
  label: string
  value: ReactNode
  icon: LucideIcon
  iconClass: string
  valueClass?: string
}

export default function StatCard({
  label,
  value,
  icon: Icon,
  iconClass,
  valueClass = 'text-3xl font-bold text-slate-900'
}: Props) : React.JSX.Element{
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <p className="text-xs text-slate-500">{label}</p>
        <Icon className={`size-5 ${iconClass}`} />
      </div>
      <p className={`mt-3 ${valueClass}`}>{value}</p>
    </div>
  )
}