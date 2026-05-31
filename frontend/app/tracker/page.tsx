"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL;

type StatusEntry = { status: string; timestamp: string };

type TrackerTicket = {
  jira_id: string;
  jira_key: string;
  jira_url: string;
  cluster_id: string;
  cluster_title: string;
  title: string;
  priority: string;
  status: string;
  created_at: string;
  pushed_at?: string;
  resolved_at?: string | null;
  shipped_at?: string | null;
  days_to_resolve?: number | null;
  status_history?: StatusEntry[];
};

function isResolved(status: string) {
  return ["done", "closed", "resolved"].includes(status.toLowerCase());
}

function fmt(ts?: string | null): string {
  if (!ts) return "—";
  return new Date(ts).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function fmtFull(ts?: string | null): string {
  if (!ts) return "—";
  return new Date(ts).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function daysOpen(ts?: string | null): number {
  if (!ts) return 0;
  return Math.max(0, Math.floor((Date.now() - new Date(ts).getTime()) / 86400000));
}

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    P1: "text-red-600 font-bold",
    P2: "text-amber-600 font-semibold",
    P3: "text-emerald-600 font-semibold",
  };
  return <span className={colors[priority] ?? "text-[#6B7280]"}>{priority}</span>;
}

function StatusBadge({ status }: { status: string }) {
  const norm = status.toLowerCase();
  if (norm === "done" || norm === "closed" || norm === "resolved")
    return <span className="text-[11px] font-bold px-3 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">Done</span>;
  if (norm.includes("progress") || norm.includes("review"))
    return <span className="text-[11px] font-bold px-3 py-0.5 rounded-full bg-amber-50 text-amber-600 border border-amber-200">In Progress</span>;
  return <span className="text-[11px] font-bold px-3 py-0.5 rounded-full bg-[#FAF8F5] text-[#6B7280] border border-[#E8E4DE]">{status || "To Do"}</span>;
}

function Timeline({ ticket }: { ticket: TrackerTicket }) {
  const resolved = isResolved(ticket.status);
  const events: { dot: string; label: string; time: string; desc: string }[] = [];

  events.push({
    dot: "bg-[#0F6E56]",
    label: "Feedback identified",
    time: fmtFull(ticket.created_at),
    desc: `"${ticket.cluster_title}" cluster surfaced by AI`,
  });

  events.push({
    dot: "bg-[#0F6E56]",
    label: "Jira ticket created",
    time: fmtFull(ticket.pushed_at || ticket.created_at),
    desc: `${ticket.jira_key} pushed to engineering`,
  });

  const history = ticket.status_history ?? [];
  for (const entry of history) {
    if (entry.status.toLowerCase() === "open") continue;
    if (resolved && entry.status.toLowerCase() === ticket.status.toLowerCase() && ticket.resolved_at) continue;
    events.push({
      dot: "bg-amber-400",
      label: `Status: ${entry.status}`,
      time: fmtFull(entry.timestamp),
      desc: "Status updated in Jira",
    });
  }

  if (resolved && ticket.resolved_at) {
    events.push({
      dot: "bg-emerald-500",
      label: "✅ Resolved",
      time: fmtFull(ticket.resolved_at),
      desc: `Fix shipped${ticket.days_to_resolve != null ? ` in ${ticket.days_to_resolve} days` : ""} — CS team notified via Slack`,
    });
  } else {
    events.push({
      dot: "bg-amber-400",
      label: `⏳ ${ticket.status || "In Progress"}`,
      time: `${daysOpen(ticket.pushed_at || ticket.created_at)} days open`,
      desc: "Waiting for engineering resolution",
    });
  }

  return (
    <div className="px-6 py-5 bg-[#FAF8F5] border-t border-[#E8E4DE]">
      <p className="text-xs font-bold text-[#6B7280] uppercase tracking-widest mb-4">
        Timeline · {ticket.title}
      </p>
      <div className="relative pl-5">
        <div className="absolute left-[7px] top-2 bottom-2 w-px bg-[#E8E4DE]" />
        <div className="space-y-5">
          {events.map((e, i) => (
            <div key={i} className="relative flex gap-4">
              <div className={`absolute -left-5 top-1 w-3 h-3 rounded-full border-2 border-white ${e.dot} shrink-0`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-[#1A1A1A]">{e.label}</span>
                  <span className="text-xs text-[#6B7280] shrink-0">{e.time}</span>
                </div>
                <p className="text-xs text-[#6B7280] mt-0.5 leading-relaxed">{e.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function Tracker() {
  const [tickets, setTickets] = useState<TrackerTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [slackSending, setSlackSending] = useState<string | null>(null);
  const [slackSent, setSlackSent] = useState<string | null>(null);
  const [slackError, setSlackError] = useState<string | null>(null);
  const [showResolved, setShowResolved] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/tracker`)
      .then((r) => r.json())
      .then(setTickets)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function sendToSlack(ticket: TrackerTicket) {
    setSlackSending(ticket.jira_id);
    setSlackError(null);
    try {
      const res = await fetch(`${API}/api/notify-slack`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket_title: ticket.title,
          cluster_title: ticket.cluster_title,
          jira_key: ticket.jira_key,
          jira_url: ticket.jira_url,
        }),
      });
      const data = await res.json();
      if (data.not_configured) {
        setSlackError(ticket.jira_id);
      } else if (data.success) {
        setSlackSent(ticket.jira_id);
        setTimeout(() => setSlackSent(null), 3000);
      }
    } catch {
      setSlackError(ticket.jira_id);
    } finally {
      setSlackSending(null);
    }
  }

  function copyNotification(ticket: TrackerTicket) {
    const msg = `Hi team — the issue "${ticket.cluster_title}" has been resolved! Jira ticket ${ticket.jira_key} is now closed. Customers affected by this issue should see the fix live shortly.`;
    navigator.clipboard.writeText(msg);
    setCopied(ticket.jira_id);
    setTimeout(() => setCopied(null), 2000);
  }

  function toggleExpand(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  const activeTickets = tickets.filter((t) => !isResolved(t.status));
  const resolvedTickets = tickets.filter((t) => isResolved(t.status));
  const resolvedWithDays = resolvedTickets.filter((t) => t.days_to_resolve != null);
  const avgDays = resolvedWithDays.length
    ? (resolvedWithDays.reduce((s, t) => s + (t.days_to_resolve ?? 0), 0) / resolvedWithDays.length).toFixed(1)
    : null;

  const stats = [
    { label: "Total pushed", value: tickets.length },
    { label: "Resolved", value: resolvedTickets.length },
    { label: "Avg time to fix", value: avgDays ? `${avgDays}d avg` : "—" },
    { label: "Open", value: activeTickets.length },
  ];

  function ActionCell({ t }: { t: TrackerTicket }) {
    if (!isResolved(t.status)) return <span className="text-[11px] text-[#6B7280] bg-[#FAF8F5] border border-[#E8E4DE] px-3 py-1 rounded-full font-medium">Awaiting resolution</span>;
    return (
      <div className="flex flex-col gap-1.5">
        <span className="text-[11px] bg-[#0F6E56]/10 text-[#0F6E56] border border-[#0F6E56]/20 font-bold px-3 py-0.5 rounded-full w-fit">Loop closed</span>
        {slackSent === t.jira_id ? (
          <span className="text-xs text-emerald-600 font-semibold">Sent to #customer-success ✓</span>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => { e.stopPropagation(); sendToSlack(t); }}
              disabled={slackSending === t.jira_id}
              className="text-xs bg-[#E8503A] hover:bg-[#d44432] disabled:opacity-50 text-white px-3 py-1 rounded-full font-semibold transition-colors"
            >
              {slackSending === t.jira_id ? "Sending…" : "Send to Slack"}
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); copyNotification(t); }}
              className="text-xs text-[#6B7280] hover:text-[#1A1A1A] font-semibold"
            >
              {copied === t.jira_id ? "Copied!" : "Copy message"}
            </button>
          </div>
        )}
        {slackError === t.jira_id && (
          <span className="text-xs text-amber-600">Add Slack webhook in settings to enable</span>
        )}
      </div>
    );
  }

  function TicketRow({ t, showTimeToFix = true }: { t: TrackerTicket; showTimeToFix?: boolean }) {
    const isExpanded = expandedId === t.jira_id;
    return (
      <>
        <tr
          key={t.jira_id}
          onClick={() => toggleExpand(t.jira_id)}
          className="border-b border-[#E8E4DE] hover:bg-[#FAF8F5] transition-colors cursor-pointer"
        >
          <td className="px-6 py-4 text-[#1A1A1A] font-medium max-w-[160px] truncate" title={t.cluster_title}>{t.cluster_title}</td>
          <td className="px-6 py-4">
            <a href={t.jira_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="text-[#E8503A] hover:underline font-semibold">
              {t.jira_key}
            </a>
            <p className="text-xs text-[#6B7280] mt-0.5 max-w-[180px] truncate">{t.title}</p>
          </td>
          <td className="px-6 py-4"><PriorityBadge priority={t.priority} /></td>
          <td className="px-6 py-4"><StatusBadge status={t.status} /></td>
          <td className="px-6 py-4 text-xs text-[#6B7280]">{fmt(t.created_at)}</td>
          {showTimeToFix ? (
            <td className="px-6 py-4 text-xs">
              {t.days_to_resolve != null
                ? <span className="text-emerald-600 font-semibold">{t.days_to_resolve}d</span>
                : <span className="text-amber-500 font-semibold">{daysOpen(t.pushed_at || t.created_at)}d open</span>}
            </td>
          ) : (
            <td className="px-6 py-4 text-xs text-[#6B7280]">{fmt(t.resolved_at)}</td>
          )}
          <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}><ActionCell t={t} /></td>
          <td className="px-6 py-4 text-[#6B7280] text-xs">{isExpanded ? "▲" : "▼"}</td>
        </tr>
        {isExpanded && (
          <tr className="border-b border-[#E8E4DE]">
            <td colSpan={8} className="p-0">
              <Timeline ticket={t} />
            </td>
          </tr>
        )}
      </>
    );
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
        <Link href="/" className="text-sm text-[#E8503A] hover:underline font-semibold">← Insights</Link>
      </nav>

      <main className="max-w-7xl mx-auto px-8 py-10">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-[#1A1A1A]">Feedback Loop Tracker</h2>
          <p className="text-sm text-[#6B7280] mt-1">Live Jira status · click any row to see full timeline</p>
        </div>

        {/* Stats bar */}
        {tickets.length > 0 && (
          <div className="flex gap-3 mb-8 flex-wrap">
            {stats.map((s) => (
              <div key={s.label} className="bg-white border border-[#E8E4DE] rounded-2xl px-5 py-3 flex flex-col gap-0.5">
                <span className="text-xl font-bold text-[#1A1A1A]">{s.value}</span>
                <span className="text-xs text-[#6B7280] font-medium">{s.label}</span>
              </div>
            ))}
          </div>
        )}

        {loading ? (
          <div className="bg-white rounded-2xl border border-[#E8E4DE] p-10 text-center">
            <svg className="animate-spin h-6 w-6 text-[#E8503A] mx-auto mb-3" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
              <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <p className="text-sm text-[#6B7280] font-medium">Loading tickets…</p>
          </div>
        ) : tickets.length === 0 ? (
          <div className="bg-white border-2 border-dashed border-[#E8E4DE] rounded-2xl p-16 text-center">
            <div className="w-12 h-12 rounded-full bg-[#FAF8F5] border border-[#E8E4DE] flex items-center justify-center mx-auto mb-4">
              <svg className="h-6 w-6 text-[#6B7280]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p className="text-[#1A1A1A] font-semibold text-sm mb-1">No tickets pushed yet</p>
            <p className="text-[#6B7280] text-xs mb-5 max-w-xs mx-auto">Generate a ticket from an insight cluster and push it to Jira to start tracking resolution time</p>
            <Link href="/" className="text-sm bg-[#E8503A] hover:bg-[#d44432] text-white px-5 py-2 rounded-full font-semibold transition-colors">
              Go to insights →
            </Link>
          </div>
        ) : (
          <>
            {/* Active tickets */}
            {activeTickets.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#E8E4DE] overflow-hidden mb-6">
                <div className="px-6 py-4 border-b border-[#E8E4DE] bg-[#FAF8F5] flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="text-xs font-bold text-[#1A1A1A] uppercase tracking-widest">In Flight — {activeTickets.length} ticket{activeTickets.length !== 1 ? "s" : ""}</span>
                </div>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#E8E4DE]">
                      {["Cluster", "Ticket", "Priority", "Status", "Created", "Time to Fix", "Action", ""].map((h) => (
                        <th key={h} className="text-left px-6 py-3 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {activeTickets.map((t) => <TicketRow key={t.jira_id} t={t} showTimeToFix={true} />)}
                  </tbody>
                </table>
              </div>
            )}

            {/* Resolved tickets */}
            {resolvedTickets.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#E8E4DE] overflow-hidden">
                <button
                  onClick={() => setShowResolved((v) => !v)}
                  className="w-full px-6 py-4 border-b border-[#E8E4DE] bg-[#FAF8F5] flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-xs font-bold text-[#1A1A1A] uppercase tracking-widest">Resolved — {resolvedTickets.length} ticket{resolvedTickets.length !== 1 ? "s" : ""}</span>
                  </div>
                  <span className="text-xs text-[#6B7280]">{showResolved ? "Hide ▲" : "Show ▼"}</span>
                </button>
                {showResolved && (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-[#E8E4DE]">
                        {["Cluster", "Ticket", "Priority", "Status", "Created", "Resolved", "Action", ""].map((h) => (
                          <th key={h} className="text-left px-6 py-3 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {resolvedTickets.map((t) => <TicketRow key={t.jira_id} t={t} showTimeToFix={false} />)}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
