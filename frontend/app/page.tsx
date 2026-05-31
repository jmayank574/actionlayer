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

const QUICK_PICKS = [
  { company: "Unwrap", product: "Customer Intelligence" },
  { company: "Slack", product: "Huddle" },
  { company: "GitHub", product: "Copilot" },
  { company: "Notion", product: "AI" },
  { company: "Jira", product: "Cloud" },
];

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
  const isPublic = cluster.source === "public";

  const severityBorder: Record<string, string> = {
    high: "border-l-red-400",
    medium: "border-l-amber-400",
    low: "border-l-emerald-400",
  };

  return (
    <div className={`bg-white rounded-2xl border border-[#E8E4DE] border-l-4 ${severityBorder[cluster.severity] ?? "border-l-gray-300"} p-6 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 space-y-4`}>
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-base font-bold text-[#1A1A1A] leading-snug">{cluster.title}</h2>
        <SeverityBadge severity={cluster.severity} />
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-[#6B7280] font-medium">{cluster.frequency} reviews</span>
        {isPublic ? (
          <div className="flex gap-1">
            {["G2", "Reddit", "App Store"].map((s) => (
              <span key={s} className="text-[10px] bg-[#FAF8F5] text-[#6B7280] border border-[#E8E4DE] px-2 py-0.5 rounded-full font-medium">
                {s}
              </span>
            ))}
          </div>
        ) : (
          <span className="text-xs text-[#6B7280]">· {cluster.source}</span>
        )}
      </div>

      <p className="text-sm text-[#1A1A1A]/75 leading-relaxed">{cluster.summary}</p>

      {cluster.ticket && (
        <Link
          href="/tracker"
          className="inline-flex items-center gap-1.5 text-[11px] font-semibold bg-amber-50 text-amber-600 border border-amber-200 px-3 py-1 rounded-full w-fit hover:bg-amber-100 transition-colors"
        >
          🔧 In progress — {cluster.ticket.jira_key}
        </Link>
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
            <svg className="h-3.5 w-3.5 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
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

      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-2">Description</p>
        <p className="text-sm text-[#1A1A1A]/80 leading-relaxed">{ticket.description}</p>
      </div>

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

      <div>
        <p className="text-[11px] font-bold text-[#6B7280] uppercase tracking-widest mb-2">Labels</p>
        <div className="flex flex-wrap gap-2">
          {ticket.labels.map((l) => (
            <span key={l} className="text-xs bg-[#FAF8F5] text-[#1A1A1A] border border-[#E8E4DE] px-3 py-0.5 rounded-full font-medium">{l}</span>
          ))}
        </div>
      </div>

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
          <a href={pushed.jira_url} target="_blank" rel="noopener noreferrer" className="text-[#E8503A] underline text-xs font-semibold">
            {pushed.jira_key} → View in Jira
          </a>
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
      <div className="flex items-center gap-2 bg-[#0F6E56]/10 border border-[#0F6E56]/20 rounded-full px-4 py-2 w-fit">
        <span className="text-xs font-bold text-[#0F6E56]">Timeline:</span>
        <span className="text-xs text-[#0F6E56]">{prd.timeline}</span>
      </div>
    </div>
  );
}

const CACHE_KEY = "actionlayer_insights_v2";

export default function Home() {
  const [clusters, setClusters] = useState<InsightCluster[]>([]);
  const [company, setCompany] = useState("Slack");
  const [product, setProduct] = useState("Huddle");
  const [lastAnalyzed, setLastAnalyzed] = useState<{ company: string; product: string } | null>(null);
  const [loadingFor, setLoadingFor] = useState<{ company: string; product: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [panel, setPanel] = useState<PanelContent>(null);
  const [generating, setGenerating] = useState<string | null>(null);

  async function handleAnalyze(co: string, prod: string) {
    setLoading(true);
    setLoadingFor({ company: co, product: prod });
    setError("");
    setClusters([]);
    try {
      const r = await fetch(
        `${API}/api/insights?company=${encodeURIComponent(co)}&product=${encodeURIComponent(prod)}`
      );
      if (!r.ok) {
        const e = await r.json().catch(() => ({}));
        throw new Error(e.detail ?? `Server error ${r.status}`);
      }
      const data = await r.json();
      if (Array.isArray(data)) {
        setClusters(data);
        setLastAnalyzed({ company: co, product: prod });
        localStorage.setItem(CACHE_KEY, JSON.stringify({ company: co, product: prod, clusters: data }));
      } else throw new Error("Unexpected response from server");
    } catch (e: any) {
      setError(e.message ?? "Failed to load insights. Is the backend running?");
    } finally {
      setLoading(false);
      setLoadingFor(null);
    }
  }

  useEffect(() => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const parsed = JSON.parse(cached);
        const co = parsed.company || "Slack";
        const prod = parsed.product || "Huddle";
        setCompany(co);
        setProduct(prod);
        setClusters(parsed.clusters || []);
        setLastAnalyzed({ company: co, product: prod });
      } else {
        handleAnalyze("Slack", "Huddle");
      }
    } catch {
      handleAnalyze("Slack", "Huddle");
    }
  }, []);

  async function handleGenerateTicket(cluster: InsightCluster) {
    setGenerating(cluster.id + "-ticket");
    try {
      const res = await fetch(`${API}/api/generate-ticket`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cluster_id: cluster.id, cluster }),
      });
      const raw = await res.json();
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
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#1A1A1A]">Analyze any product</h2>
          <p className="text-sm text-[#6B7280] mt-1">
            {lastAnalyzed && clusters.length > 0
              ? `${clusters.length} issue clusters · ${lastAnalyzed.product} by ${lastAnalyzed.company} · Powered by Claude's knowledge of public reviews`
              : "Powered by Claude's knowledge of public reviews"}
          </p>

          <div className="flex flex-wrap gap-2 mt-4">
            {QUICK_PICKS.map((p) => (
              <button
                key={p.company + p.product}
                onClick={() => {
                  setCompany(p.company);
                  setProduct(p.product);
                  handleAnalyze(p.company, p.product);
                }}
                disabled={loading}
                className={`text-xs px-3 py-1.5 rounded-full font-semibold border transition-colors disabled:opacity-40 ${
                  lastAnalyzed?.company === p.company && lastAnalyzed?.product === p.product
                    ? "bg-[#0F6E56]/10 text-[#0F6E56] border-[#0F6E56]/20"
                    : "bg-white text-[#6B7280] border-[#E8E4DE] hover:border-[#1A1A1A] hover:text-[#1A1A1A]"
                }`}
              >
                {p.company} · {p.product}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 mt-4">
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && company.trim() && product.trim() && handleAnalyze(company, product)}
              placeholder="Company"
              className="text-sm border border-[#E8E4DE] rounded-full px-4 py-2 focus:outline-none focus:border-[#E8503A] w-40 bg-white text-[#1A1A1A]"
            />
            <input
              value={product}
              onChange={(e) => setProduct(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && company.trim() && product.trim() && handleAnalyze(company, product)}
              placeholder="Product"
              className="text-sm border border-[#E8E4DE] rounded-full px-4 py-2 focus:outline-none focus:border-[#E8503A] w-40 bg-white text-[#1A1A1A]"
            />
            <button
              onClick={() => handleAnalyze(company, product)}
              disabled={loading || !company.trim() || !product.trim()}
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
              ) : (
                "Analyze →"
              )}
            </button>
          </div>
        </div>

        {loading && loadingFor && (
          <div className="bg-white border border-[#E8E4DE] rounded-2xl px-5 py-4 mb-6 flex items-center gap-3">
            <svg className="animate-spin h-4 w-4 text-[#E8503A] shrink-0" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-[#1A1A1A]">
                Analyzing public feedback for {loadingFor.product} by {loadingFor.company}…
              </p>
              <p className="text-xs text-[#6B7280] mt-0.5">
                Searching G2, Reddit, App Store, Twitter · May take up to 20 seconds
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 text-sm text-red-600 font-medium mb-8">
            {error}
          </div>
        )}

        {!loading && clusters.length === 0 && !error && (
          <div className="bg-white border-2 border-dashed border-[#E8E4DE] rounded-2xl p-16 text-center">
            <p className="text-[#6B7280] text-sm font-medium">
              Select a product above or type a company and product to analyze
            </p>
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
          <aside className="fixed right-0 top-0 h-full w-[440px] bg-white border-l border-[#E8E4DE] z-50 flex flex-col shadow-xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#E8E4DE] bg-[#FAF8F5]">
              <span className="text-sm font-bold text-[#1A1A1A]">
                {panel?.type === "ticket" ? "Jira Ticket Draft" : panel?.type === "prd" ? "Product Requirements Doc" : "Generating with Claude…"}
              </span>
              <button
                onClick={() => setPanel(null)}
                className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-[#E8E4DE] transition-colors text-[#6B7280] hover:text-[#1A1A1A]"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 6L6 18M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-6">
              {generating ? (
                <div className="flex flex-col items-center justify-center h-48 gap-4">
                  <svg className="animate-spin h-8 w-8 text-[#E8503A]" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                    <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  <p className="text-sm text-[#6B7280] font-medium">
                    Claude is writing your {generating?.includes("prd") ? "PRD" : "ticket"}…
                  </p>
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
