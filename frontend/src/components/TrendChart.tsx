import { Bar, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { TrendPoint } from '../types'
import type { TrendStatus } from '../lib/trends'
import { COLORS } from '../lib/theme'

const LINE_COLOR: Record<TrendStatus, string> = {
  rising: COLORS.rust,
  falling: COLORS.sage,
  stable: COLORS.inkSoft,
  unknown: COLORS.rust, // "watching" cards still read as an active/warm chart, not a neutral gray one
}

const BAR_COLOR: Record<TrendStatus, string> = {
  rising: COLORS.rustBar,
  falling: COLORS.sageBar,
  stable: '#e7e5e4', // stone-200
  unknown: COLORS.rustBar,
}

// Low-volume periods (adequate_volume: false) get a lighter/hollow-feeling
// dot instead of the normal filled one -- a visual tell that a point rests
// on too few reviews to trust on its own.
function LowVolumeDot(props: { cx?: number; cy?: number; payload?: TrendPoint; color: string }) {
  const { cx, cy, payload, color } = props
  if (cx == null || cy == null) return null
  const adequate = payload?.adequate_volume ?? true
  return adequate ? (
    <circle cx={cx} cy={cy} r={3} fill="white" stroke={color} strokeWidth={2} />
  ) : (
    <circle cx={cx} cy={cy} r={3} fill="var(--color-cream-raised)" stroke={color} strokeWidth={1.5} strokeDasharray="2 1" />
  )
}

export default function TrendChart({
  data,
  status = 'unknown',
  compact = false,
}: {
  data: TrendPoint[]
  status?: TrendStatus
  compact?: boolean
}) {
  const line = LINE_COLOR[status]
  const bar = BAR_COLOR[status]
  const hasLowVolume = data.some((d) => !d.adequate_volume)

  return (
    <div>
      <ResponsiveContainer width="100%" height={compact ? 84 : 200}>
        <ComposedChart data={data} margin={compact ? { top: 6, right: 4, bottom: 0, left: 4 } : { top: 10, right: 8, bottom: 0, left: 0 }}>
          <XAxis
            dataKey="period"
            hide={compact}
            tick={{ fontSize: 10, fill: '#a8a29e' }}
            axisLine={false}
            tickLine={false}
            minTickGap={20}
          />
          <YAxis
            hide={compact}
            tick={{ fontSize: 10, fill: '#a8a29e' }}
            width={30}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
            domain={[0, 'auto']}
          />
          {!compact && (
            <Tooltip
              cursor={{ fill: 'rgba(0,0,0,0.03)' }}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e7e5e4' }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`, 'rate']}
              labelFormatter={(label) => `${label}`}
            />
          )}
          <Bar dataKey="rate_pct" fill={bar} radius={[4, 4, 0, 0]} maxBarSize={compact ? 16 : 34} isAnimationActive={false} />
          <Line
            type="monotone"
            dataKey="rate_pct"
            stroke={line}
            strokeWidth={compact ? 1.75 : 2.25}
            dot={compact ? false : (props) => <LowVolumeDot key={props.payload?.period} {...props} color={line} />}
            isAnimationActive={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
      {!compact && hasLowVolume && (
        <p className="mt-1 text-[11px] text-stone-400">
          Hollow points mark months with fewer than 30 reviews — read those as directional, not
          precise.
        </p>
      )}
    </div>
  )
}
