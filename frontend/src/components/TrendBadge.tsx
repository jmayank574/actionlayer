import type { TrendStatus } from '../lib/trends'

const STYLES: Record<TrendStatus, { label: string; className: string }> = {
  rising: { label: '▲ rising', className: 'bg-rust-50 text-rust-700 border-rust-100' },
  falling: { label: '▼ falling', className: 'bg-sage-50 text-sage-700 border-sage-100' },
  stable: { label: '● stable', className: 'bg-stone-100 text-stone-500 border-stone-200' },
  unknown: { label: '— n/a', className: 'bg-stone-50 text-stone-400 border-stone-100' },
}

export default function TrendBadge({ status, title }: { status: TrendStatus; title?: string }) {
  const s = STYLES[status]
  return (
    <span
      title={title}
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium tabular-nums ${s.className}`}
    >
      {s.label}
    </span>
  )
}
