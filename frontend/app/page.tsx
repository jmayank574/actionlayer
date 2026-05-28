"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL;

type TicketRef = {
  jira_key: string;
  jira_url: string;
  status: string;
};

type InsightCluster = {
  id: string;
  title: string;
  severity: "high" | "medium" | "low";
  frequency: number;
  summary: string;
  verbatims: string[];
  source: string;
  ticket: TicketRef | null;
};

type GeneratedTicket = {
  title: string;
  description: string;
  acceptanceCriteria: string[];
  priority: string;
  storyPoints: number;
  labels: string[];
  customerQuotes: string[];
};

type GeneratedPRD = {
  title: string;
  problemStatement: string;
  userPersona: string;
  businessImpact: string;
  proposedSolution: string;
  outOfScope: string;
  successMetrics: string[];
  timeline: string;
};

type PanelContent =
  | { type: "ticket"; data: GeneratedTicket; cluster: InsightCluster }
  | { type: "prd"; data: GeneratedPRD; cluster: InsightCluster }
  | null;

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    high: "bg-red-50 text-red-600 border border-red-200",
    medium: "bg-amber-50 text-amber-600 border border-amber-200",
    low: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  };
  return (
    <span className={`text-[11px] font-bold px-3 py-0.5 rounded-full tracking-wide ${colors[severity] ?? "bg-gray-100 text-gray-500"}`}>
      {severity.toUpperCase()}
    </span>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl border border-[#E8E4DE] p-6 animate-pulse space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div className="h-4 bg-[#E8E4DE] rounded-full w-2/3" />
        <div className="h-5 bg-[#E8E4DE] rounded-full w-14" />
      </div>
      <div className="h-3 bg-[#E8E4DE] rounded-full w-1/4" />
      <div className="space-y-2">
        <div className="h-3 bg-[#E8E4DE] rounded-full w-full" />
        <div className="h-3 bg-[#E8E4DE] rounded-full w-5/6" />
      </div>
      <div className="flex gap-2 pt-1">
        <div className="h-9 bg-[#E8E4DE] rounded-full w-36" />
        <div className="h-9 bg-[#E8E4DE] rounded-full w-32" />
      </div>
    </div>
  );
}

function InsightCard({
  cluster,
  onGenerateTicket,
  onGeneratePRD,
}: {
  cluster: InsightCluster;
  onGenerateTicket: (c: InsightCluster) => void;
  onGeneratePRD: (c: InsightCluster) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-2xl border border-[#E8E4DE] p-6 hover:border-[#E8503A] transition-colors duration-200 space-y-4">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-base font-bold text-[#1A1A1A] leading-snug">{cluster.title}</h2>
        <SeverityBadge severity={cluster.severity} />
      </div>
      <p className="text-xs text-[#6B7280] font-medium">{cluster.frequency} tickets · {cluster.source}</p>
      <p className="text-sm text-[#1A1A1A]/75 leading-relaxed">{cluster.summary}</p>

      {cluster.ticket && (
        <a
          href="/tracker"
          className="inline-flex items-center gap-1.5 text-[11px] font-semibold bg-amber-50 text-amber-600 border border-amber-200 px-3 py-1 rounded-full w-fit hover:bg-amber-100 transition-colors"
        >
          🔧 In progress — {cluster.ticket.jira_key}
        </a>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-[#E8503A] font-semibold hover:underline"
      >
        {expanded ? "Hide quotes ↑" : "Show customer quotes ↓"}
      </button>

      {expanded && (
        <ul className="space-y-2 pt-1">
          {cluster.verbatims.map((v, i) => (
            <li key={i} className="text-xs text-[#6B7280] italic border-l-2 border-[#E8503A]/30 pl-3 leading-relaxed">
              &quot;{v}&quot;
            </li>
          ))}
        </ul>
      )}

      <div className="flex gap-2 pt-1">
        {cluster.ticket ? (
          <button
            disabled
            className="text-sm flex items-center gap-1.5 bg-[#FAF8F5] text-[#6B7280] border border-[#E8E4DE] px-4 py-2 rounded-full font-semibold cursor-not-allowed"
          >
            <svg className="h-3.5 w-3.5 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round"/></svg>
            Ticket pushed
          </button>
        ) : (
          <button
            onClick={() => onGenerateTicket(cluster)}
            className="text-sm bg-[#E8503A] hover:bg-[#d44432] text-white px-4 py-2 rounded-full font-semibold transition-colors"
          >
            Generate ticket
          </button>
        )}
        <button
          onClick={() => onGeneratePRD(cluster)}
          className="text-sm bg-white text-[#1A1A1A] border border-[#E8E4DE] hover:border-[#1A1A1A] px-4 py-2 rounded-full font-semibold transition-colors"
        >
          Generate PRD
        </button>
      </div>
    </div>
  );
}

function TicketPanel({ ticket, cluster }: { ticket: GeneratedTicket; cluster: InsightCluster }) {
  const [pushing, setPushing] = useState(false);
  const [pushed, setPushed] = useState<{ jira_key: string; jira_url: string } | null>(null);
  const [error, setError] = useState("");

  async function pushToJira() {
    setPushing(true);
    setError("");
    try {
      const res = await fetch(`${API}/api/push-to-jira`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket, cluster_id: cluster.id, cluster_title: cluster.title }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setPushed(data);
    } catch (e: any) {
      setError(e.message ?? "Push failed");
    } finally {
      setPushing(false);
    }
  }

  const priorityStyles: Record<string, string> = {
    P1: "bg-red-50 text-red-600 border border-red-200",
    P2: "bg-amber-50 text-amber-600 border border-amber-200",
    P3: "bg-emerald-50 text-emerald-700 border border-emerald-200",
  };

  return (
    <div className="space-y-6">
      {/* Title + priority */}
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <h2 className="text-base font-bold text-[#1A1A1A] leading-snug">{ticket.title}</h2>
          <span className={`shrink-0 text-[11px] font-bold px-3 py-0.5 rounded-full ${priorityStyles[ticket.priority] ?? "bg-gray-100 text-gray-500"}`}>
            {ticket.priority}
          </span>
        </div>
        <span className="inline-block text-xs bg-[#E8503A]/10 text-[#E8503A] font-semibold px-3 py-0.5 rounded-full">
          {ticket.storyPoints} story points
        </span>
      </div>

      {/* Description */}
      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-2">Description</p>
        <p className="text-sm text-[#1A1A1A]/80 leading-relaxed">{ticket.description}</p>
      </div>

      {/* Acceptance Criteria */}
      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-3">Acceptance Criteria</p>
        <ol className="space-y-3">
          {ticket.acceptanceCriteria.map((ac, i) => (
            <li key={i} className="flex gap-3 text-xs text-[#1A1A1A]/80">
              <span className="shrink-0 w-5 h-5 rounded-full bg-[#E8503A]/10 text-[#E8503A] font-bold flex items-center justify-center text-[10px]">{i + 1}</span>
              <span className="leading-relaxed pt-0.5">{ac}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Labels */}
      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-2">Labels</p>
        <div className="flex flex-wrap gap-2">
          {ticket.labels.map((l) => (
            <span key={l} className="text-xs bg-[#FAF8F5] text-[#1A1A1A] border border-[#E8E4DE] px-3 py-0.5 rounded-full font-medium">{l}</span>
          ))}
        </div>
      </div>

      {/* Customer Quotes */}
      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-3">Customer Quotes</p>
        <div className="space-y-3">
          {ticket.customerQuotes.map((q, i) => (
            <blockquote key={i} className="border-l-2 border-[#E8503A]/40 pl-3 text-xs text-[#6B7280] italic leading-relaxed">
              &quot;{q}&quot;
            </blockquote>
          ))}
        </div>
      </div>

      {pushed ? (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4">
          <p className="font-bold text-emerald-700 text-sm mb-1">Pushed to Jira!</p>
          <a href={pushed.jira_url} target="_blank" rel="noopener noreferrer" className="text-[#E8503A] underline text-xs font-semibold">{pushed.jira_key} → View in Jira</a>
        </div>
      ) : (
        <>
          {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
          <button
            onClick={pushToJira}
            disabled={pushing}
            className="w-full bg-[#E8503A] hover:bg-[#d44432] disabled:opacity-50 text-white text-sm py-3 rounded-full font-semibold transition-colors"
          >
            {pushing ? "Pushing to Jira…" : "Push to Jira"}
          </button>
        </>
      )}
    </div>
  );
}

function PRDPanel({ prd }: { prd: GeneratedPRD }) {
  return (
    <div className="space-y-6">
      <h3 className="text-base font-bold text-[#1A1A1A] leading-snug">{prd.title}</h3>
      {[
        ["Problem Statement", prd.problemStatement],
        ["User Persona", prd.userPersona],
        ["Business Impact", prd.businessImpact],
        ["Proposed Solution", prd.proposedSolution],
        ["Out of Scope", prd.outOfScope],
      ].map(([label, value]) => (
        <div key={label}>
          <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-2">{label}</p>
          <p className="text-sm text-[#1A1A1A]/80 leading-relaxed">{value}</p>
        </div>
      ))}
      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-3">Success Metrics</p>
        <ul className="space-y-2">
          {prd.successMetrics.map((m, i) => (
            <li key={i} className="text-xs text-[#1A1A1A]/80 flex gap-2 leading-relaxed">
              <span className="text-[#E8503A] font-bold shrink-0">›</span>{m}
            </li>
          ))}
        </ul>
      </div>
      <div className="flex items-center gap-2 bg-[#0F6E56]/8 border border-[#0F6E56]/20 rounded-full px-4 py-2 w-fit">
        <span className="text-xs font-bold text-[#0F6E56]">Timeline:</span>
        <span className="text-xs text-[#0F6E56]">{prd.timeline}</span>
      </div>
    </div>
  );
}

const CACHE_KEY = "actionlayer_clusters";

export default function Home() {
  const [clusters, setClusters] = useState<InsightCluster[]>([]);

  useEffect(() => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) setClusters(JSON.parse(cached));
    } catch {}
  }, []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [panel, setPanel] = useState<PanelContent>(null);
  const [generating, setGenerating] = useState<string | null>(null);
  const [pasteOpen, setPasteOpen] = useState(false);
  const [pasteText, setPasteText] = useState("");
  const [clusterSource, setClusterSource] = useState<"zendesk" | "csv">("zendesk");

  async function fetchInsights() {
    setLoading(true);
    setError("");
    setClusters([]);
    setPasteOpen(false);
    try {
      const r = await fetch(`${API}/api/insights`);
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail ?? `Server error ${r.status}`);
      }
      const data = await r.json();
      if (Array.isArray(data)) {
        setClusters(data);
        setClusterSource("zendesk");
        localStorage.setItem(CACHE_KEY, JSON.stringify(data));
      } else throw new Error("Unexpected response from server");
    } catch (e: any) {
      setError(e.message ?? "Failed to load insights. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function handleIngestCSV() {
    if (!pasteText.trim()) return;
    setLoading(true);
    setError("");
    setClusters([]);
    try {
      const r = await fetch(`${API}/api/ingest-csv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: pasteText }),
      });
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail ?? `Server error ${r.status}`);
      }
      const data = await r.json();
      if (Array.isArray(data)) {
        setClusters(data);
        setClusterSource("csv");
        setPasteOpen(false);
        localStorage.setItem(CACHE_KEY, JSON.stringify(data));
      } else throw new Error("Unexpected response from server");
    } catch (e: any) {
      setError(e.message ?? "Failed to analyze feedback. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateTicket(cluster: InsightCluster) {
    setGenerating(cluster.id + "-ticket");
    try {
      const res = await fetch(`${API}/api/generate-ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cluster_id: cluster.id, cluster }),
      });
      const raw = await res.json();
      console.log("[generate-ticket] status:", res.status, "raw:", JSON.stringify(raw, null, 2));
      if (!res.ok) {
        setPanel({ type: "error", message: raw.detail ?? `Server error ${res.status}`, cluster } as any);
        return;
      }
      const data: GeneratedTicket = {
        title: raw.title ?? raw.Title ?? "",
        description: raw.description ?? raw.Description ?? "",
        priority: raw.priority ?? raw.Priority ?? "P2",
        storyPoints: raw.storyPoints ?? raw.story_points ?? raw.StoryPoints ?? 3,
        acceptanceCriteria: raw.acceptanceCriteria ?? raw.acceptance_criteria ?? raw.AcceptanceCriteria ?? [],
        labels: raw.labels ?? raw.Labels ?? [],
        customerQuotes: raw.customerQuotes ?? raw.customer_quotes ?? raw.CustomerQuotes ?? [],
      };
      setPanel({ type: "ticket", data, cluster });
    } catch (e: any) {
      setPanel({ type: "error", message: e.message ?? "Unknown error", cluster } as any);
    } finally {
      setGenerating(null);
    }
  }

  async function handleGeneratePRD(cluster: InsightCluster) {
    setGenerating(cluster.id + "-prd");
    try {
      const res = await fetch(`${API}/api/generate-prd`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cluster_id: cluster.id, cluster }),
      });
      const raw = await res.json();
      console.log("[generate-prd] status:", res.status, "raw:", JSON.stringify(raw, null, 2));
      if (!res.ok) {
        setPanel({ type: "error", message: raw.detail ?? `Server error ${res.status}`, cluster } as any);
        return;
      }
      setPanel({ type: "prd", data: raw, cluster });
    } catch (e: any) {
      setPanel({ type: "error", message: e.message ?? "Unknown error", cluster } as any);
    } finally {
      setGenerating(null);
    }
  }

  const loadInsightsButton = clusterSource !== "csv" ? (
    <button
      onClick={fetchInsights}
      disabled={loading}
      className="flex items-center gap-2 bg-[#E8503A] hover:bg-[#d44432] disabled:opacity-50 text-white text-sm px-5 py-2.5 rounded-full font-semibold transition-colors"
    >
      {loading ? (
        <>
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          Analyzing…
        </>
      ) : (
        <>
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          {clusters.length > 0 ? "Refresh Insights" : "Load Insights"}
        </>
      )}
    </button>
  ) : null;

  return (
    <div className="min-h-screen bg-[#FAF8F5]">
      <nav className="bg-white border-b border-[#E8E4DE] px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-xl font-bold text-[#1A1A1A] tracking-tight">ActionLayer</h1>
            <p className="text-xs text-[#6B7280]">Feedback → Engineering, automated.</p>
          </div>
          <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-[#0F6E56]/10 text-[#0F6E56] border border-[#0F6E56]/20 tracking-wide">
            Built on Claude API
          </span>
        </div>
        <Link href="/tracker" className="text-sm text-[#E8503A] hover:underline font-semibold">
          Loop Tracker →
        </Link>
      </nav>

      <main className="max-w-5xl mx-auto px-8 py-10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-[#1A1A1A]">Insight Clusters</h2>
            <p className="text-sm text-[#6B7280] mt-1">
              {clusters.length > 0
                ? `AI-grouped feedback from ${clusterSource === "csv" ? "Zendesk + Unwrap" : "Zendesk"} · ${clusters.length} clusters`
                : "Pull your Zendesk tickets or paste feedback from Unwrap"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => { setPasteOpen((o) => !o); setError(""); }}
              disabled={loading}
              className="flex items-center gap-2 bg-white text-[#1A1A1A] border border-[#E8E4DE] hover:border-[#1A1A1A] disabled:opacity-50 text-sm px-4 py-2.5 rounded-full font-semibold transition-colors"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Import from Unwrap
            </button>
            {loadInsightsButton}
          </div>
        </div>

        {pasteOpen && (
          <div className="bg-white border border-[#E8E4DE] rounded-2xl p-5 mb-6 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-[#1A1A1A]">Paste customer feedback</p>
              <span className="text-xs text-[#6B7280]">One item per line — paste a CSV export, Unwrap data, or raw feedback</span>
            </div>
            <textarea
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder={"App crashes on login after update\nPayment failed but I was still charged\nCan't find the dark mode setting\nSearch results don't match what I'm typing"}
              rows={6}
              className="w-full text-sm border border-[#E8E4DE] rounded-xl px-4 py-3 resize-none focus:outline-none focus:border-[#E8503A] text-[#1A1A1A] placeholder-[#C4BDB5] font-mono leading-relaxed"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-[#6B7280]">{pasteText.split("\n").filter((l) => l.trim()).length} feedback items</span>
              <div className="flex gap-2">
                <button
                  onClick={() => { setPasteOpen(false); setPasteText(""); }}
                  className="text-sm text-[#6B7280] hover:text-[#1A1A1A] px-4 py-2 rounded-full font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleIngestCSV}
                  disabled={loading || !pasteText.trim()}
                  className="flex items-center gap-2 bg-[#E8503A] hover:bg-[#d44432] disabled:opacity-50 text-white text-sm px-5 py-2 rounded-full font-semibold transition-colors"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                      Analyzing…
                    </>
                  ) : "Analyze Feedback"}
                </button>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-sm text-red-600 font-medium mb-8">{error}</div>
        )}

        {!loading && clusters.length === 0 && !error && !pasteOpen && (
          <div className="bg-white border-2 border-dashed border-[#E8E4DE] rounded-2xl p-16 text-center">
            <p className="text-[#6B7280] text-sm font-medium">Click "Load Insights" to pull Zendesk tickets, or "Import from Unwrap" to paste feedback</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
            : clusters.map((c) => (
                <InsightCard
                  key={c.id}
                  cluster={c}
                  onGenerateTicket={handleGenerateTicket}
                  onGeneratePRD={handleGeneratePRD}
                />
              ))}
        </div>
      </main>

      {(panel || generating) && (
        <>
          <div className="fixed inset-0 bg-[#1A1A1A]/30 z-40" onClick={() => setPanel(null)} />
          <aside className="fixed right-0 top-0 h-full w-[440px] bg-white border-l border-[#E8E4DE] z-50 flex flex-col">
            <div className="flex items-center justify-between px-6 py-5 border-b border-[#E8E4DE]">
              <span className="text-sm font-bold text-[#1A1A1A]">
                {panel?.type === "ticket" ? "Jira Ticket Draft" : panel?.type === "prd" ? "Product Requirements Doc" : "Generating with Claude…"}
              </span>
              <button onClick={() => setPanel(null)} className="text-[#6B7280] hover:text-[#1A1A1A] text-lg leading-none font-light">✕</button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-6">
              {generating ? (
                <div className="flex flex-col items-center justify-center h-48 gap-4">
                  <svg className="animate-spin h-8 w-8 text-[#E8503A]" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                    <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <p className="text-sm text-[#6B7280] font-medium">Claude is writing your {generating?.includes("prd") ? "PRD" : "ticket"}…</p>
                </div>
              ) : (panel as any)?.type === "error" ? (
                <div className="space-y-3">
                  <p className="text-sm font-bold text-red-600">Generation failed</p>
                  <p className="text-xs text-[#6B7280] leading-relaxed">{(panel as any).message}</p>
                  <p className="text-xs text-[#6B7280]">Check the backend terminal for the full error, then try again.</p>
                </div>
              ) : panel?.type === "ticket" ? (
                <TicketPanel ticket={panel.data} cluster={panel.cluster} />
              ) : panel?.type === "prd" ? (
                <PRDPanel prd={panel.data} />
              ) : null}
            </div>
          </aside>
        </>
      )}
    </div>
  );
}
