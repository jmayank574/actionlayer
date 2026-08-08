import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import TrendChart from '../components/TrendChart'
import { askAssistant } from '../lib/assistant'
import type { AskResponse, ChatMessage } from '../lib/assistant'
import type { TrendStatus } from '../lib/trends'

interface Turn {
  question: string
  response: AskResponse | null
  error: string | null
}

function chartStatus(series: AskResponse['chart']): TrendStatus {
  if (!series || series.series.length === 0) return 'unknown'
  const last = series.series[series.series.length - 1]
  if (last.flagged_spike) return 'rising'
  if (last.flagged_decline) return 'falling'
  return 'stable'
}

function QuoteRow({ quote }: { quote: AskResponse['quotes'][number] }) {
  return (
    <p className="text-[13.5px] text-stone-600 leading-relaxed">
      "{quote.text}"{' '}
      <span className="whitespace-nowrap text-stone-400">
        — {quote.rating != null ? `${quote.rating}★, ` : ''}
        {quote.date?.slice(0, 10)} · {quote.source === 'google_play' ? 'Play' : 'App Store'}
      </span>
    </p>
  )
}

export default function Assistant() {
  const [input, setInput] = useState('')
  const [turns, setTurns] = useState<Turn[]>([])
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const question = input.trim()
    if (!question || loading) return
    setInput('')
    setLoading(true)

    const priorMessages: ChatMessage[] = turns.flatMap((t) =>
      t.response
        ? [
            { role: 'user' as const, content: t.question },
            { role: 'assistant' as const, content: t.response.text },
          ]
        : [],
    )

    setTurns((prev) => [...prev, { question, response: null, error: null }])

    try {
      const response = await askAssistant([...priorMessages, { role: 'user', content: question }])
      setTurns((prev) => {
        const next = [...prev]
        next[next.length - 1] = { question, response, error: null }
        return next
      })
    } catch (err) {
      setTurns((prev) => {
        const next = [...prev]
        next[next.length - 1] = {
          question,
          response: null,
          error: err instanceof Error ? err.message : 'Something went wrong.',
        }
        return next
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <span className="inline-block rounded-full bg-rust-50 px-3 py-1 text-[11px] font-medium text-rust-600">
          Assistant
        </span>
        <h1 className="mt-3 font-serif text-3xl font-semibold text-stone-900">Ask questions. Get answers.</h1>
        <p className="mt-2 max-w-xl text-sm text-stone-500 leading-relaxed">
          Type a question in plain language about WHOOP's real reviews and get an answer grounded in actual
          data — real quotes, real rates, real trends. Nothing here is invented; every number and quote traces
          back to a review the Assistant looked up while answering.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-3 shadow-sm">
        <Search size={17} className="shrink-0 text-stone-400" />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What's driving complaints about app stability?"
          className="flex-1 bg-transparent text-[14.5px] text-stone-800 placeholder:text-stone-400 focus:outline-none"
          disabled={loading}
        />
        {loading && <Loader2 size={16} className="shrink-0 animate-spin text-rust-500" />}
      </form>

      <div className="space-y-10">
        {turns.map((turn, i) => (
          <div key={i} className="space-y-4">
            <p className="font-serif text-lg text-stone-800">{turn.question}</p>

            {turn.error && (
              <p className="rounded-xl border border-rust-100 bg-rust-50 px-4 py-3 text-sm text-rust-600">
                {turn.error}
                {turn.error.includes(':8001') && (
                  <>
                    {' '}Run <code className="rounded bg-white px-1 py-0.5 text-[12px]">uvicorn assistant_server:app --reload --port 8001</code> in{' '}
                    <code className="rounded bg-white px-1 py-0.5 text-[12px]">backend/</code>.
                  </>
                )}
              </p>
            )}

            {!turn.response && !turn.error && (
              <p className="flex items-center gap-2 text-sm text-stone-400">
                <Loader2 size={14} className="animate-spin" /> Researching real reviews and stats…
              </p>
            )}

            {turn.response && (
              <div className="rounded-2xl bg-white p-6 shadow-[0_1px_2px_rgba(23,20,15,0.06),0_8px_24px_rgba(23,20,15,0.04)]">
                <div className="prose prose-sm prose-stone max-w-none prose-headings:font-serif prose-headings:font-semibold prose-table:text-[13px] prose-th:text-stone-500 prose-strong:text-stone-800">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{turn.response.text}</ReactMarkdown>
                </div>

                {(turn.response.chart || turn.response.quotes.length > 0) && (
                  <div className="mt-5 grid grid-cols-1 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.15fr)] gap-6 items-start border-t border-stone-100 pt-5">
                    {turn.response.chart && (
                      <div>
                        <p className="mb-1 text-[11px] text-stone-400">
                          {turn.response.chart.category_name} · {turn.response.chart.scope}
                        </p>
                        <TrendChart data={turn.response.chart.series} status={chartStatus(turn.response.chart)} />
                      </div>
                    )}
                    {turn.response.quotes.length > 0 && (
                      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
                        {turn.response.quotes.map((q) => (
                          <QuoteRow key={q.review_id} quote={q} />
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {turns.length === 0 && (
        <div className="rounded-2xl border border-dashed border-stone-200 px-6 py-10 text-center">
          <p className="text-sm text-stone-400">
            Try: "What's driving complaints about app stability?" or "Show me the trend for AI Coach mentions."
          </p>
        </div>
      )}
    </div>
  )
}
