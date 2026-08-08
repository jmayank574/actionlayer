import type { TrendPoint } from '../types'

// The Assistant is the one live-backend feature in this app -- everything
// else reads static JSON. Local-dev-only for now: run
// `uvicorn assistant_server:app --reload --port 8001` in backend/ alongside
// `npm run dev`. See CLAUDE.md.
const ASSISTANT_API_URL = 'http://localhost:8001'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AssistantQuote {
  review_id: string
  source: 'google_play' | 'app_store'
  rating: number | null
  date: string
  text: string
  categories: string[]
}

export interface AssistantChart {
  category_id: string
  category_name: string
  scope: string
  series: TrendPoint[]
}

export interface AssistantCategoryStat {
  category_id: string
  category_name: string
  level: 'parent' | 'subcategory'
  scope: string
  recent_rate_pct: number
  baseline_rate_pct: number
  pp_delta: number
  ratio: number | null
  recent_count: number
  baseline_count: number
  verdict: string
  flagged_spike: boolean
  flagged_decline: boolean
}

export interface AskResponse {
  text: string
  quotes: AssistantQuote[]
  chart: AssistantChart | null
  category_stats: AssistantCategoryStat[]
}

export async function askAssistant(messages: ChatMessage[]): Promise<AskResponse> {
  const res = await fetch(`${ASSISTANT_API_URL}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  })
  if (!res.ok) {
    throw new Error(`Assistant request failed (${res.status}) -- is the backend running on :8001?`)
  }
  return res.json()
}
