"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL;

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
};

function StatusBadge({ status }: { status: string }) {
  const norm = status.toLowerCase();
  if (norm === "done" || norm === "closed" || norm === "resolved") {
    return <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-bold px-3 py-0.5 rounded-full">Done</span>;
  }
  if (norm.includes("progress") || norm.includes("review")) {
    return <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-600 border border-amber-200 text-[11px] font-bold px-3 py-0.5 rounded-full">In Progress</span>;
  }
  return <span className="inline-flex items-center gap-1 bg-[#FAF8F5] text-[#6B7280] border border-[#E8E4DE] text-[11px] font-bold px-3 py-0.5 rounded-full">{status || "To Do"}</span>;
}

function daysOpen(created_at: string): number {
  if (!created_at) return 0;
  const ms = Date.now() - new Date(created_at).getTime();
  return Math.max(0, Math.floor(ms / (1000 * 60 * 60 * 24)));
}

function isLoopClosed(status: string): boolean {
  const norm = status.toLowerCase();
  return norm === "done" || norm === "closed" || norm === "resolved";
}

export default function Tracker() {
  const [tickets, setTickets] = useState<TrackerTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);
  const [slackSending, setSlackSending] = useState<string | null>(null);
  const [slackSent, setSlackSent] = useState<string | null>(null);
  const [slackError, setSlackError] = useState<string | null>(null);

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

  const priorityColor: Record<string, string> = {
    P1: "text-red-600 font-bold",
    P2: "text-yellow-600 font-semibold",
    P3: "text-green-600",
  };

  return (
    <div className="min-h-screen bg-[#FAF8F5]">
      <nav className="bg-white border-b border-[#E8E4DE] px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#1A1A1A] tracking-tight">ActionLayer</h1>
          <p className="text-xs text-[#6B7280]">Feedback → Engineering, automated.</p>
        </div>
        <Link href="/" className="text-sm text-[#E8503A] hover:underline font-semibold">
          ← Back to Insights
        </Link>
      </nav>

      <main className="max-w-6xl mx-auto px-8 py-10">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#1A1A1A]">Feedback Loop Tracker</h2>
          <p className="text-sm text-[#6B7280] mt-1">Live Jira status for all pushed tickets · {tickets.length} tracked</p>
        </div>

        {loading ? (
          <div className="bg-white rounded-2xl border border-[#E8E4DE] p-10 text-center">
            <div className="flex justify-center mb-3">
              <svg className="animate-spin h-6 w-6 text-[#E8503A]" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
            </div>
            <p className="text-sm text-[#6B7280] font-medium">Loading tickets…</p>
          </div>
        ) : tickets.length === 0 ? (
          <div className="bg-white rounded-2xl border-2 border-dashed border-[#E8E4DE] p-16 text-center">
            <p className="text-[#6B7280] text-sm font-medium">No tickets pushed yet. Go to <Link href="/" className="text-[#E8503A] underline font-semibold">Insights</Link> to generate and push your first ticket.</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-[#E8E4DE] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#E8E4DE] bg-[#FAF8F5]">
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Cluster</th>
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Ticket</th>
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Priority</th>
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Status</th>
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Days Open</th>
                  <th className="text-left px-6 py-4 text-[11px] font-bold text-[#6B7280] uppercase tracking-widest">Action</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((t) => (
                  <tr key={t.jira_id} className="border-b border-[#E8E4DE] hover:bg-[#FAF8F5] transition-colors">
                    <td className="px-6 py-4 text-[#1A1A1A] font-medium max-w-[180px] truncate" title={t.cluster_title}>{t.cluster_title}</td>
                    <td className="px-6 py-4">
                      <a href={t.jira_url} target="_blank" rel="noopener noreferrer" className="text-[#E8503A] hover:underline font-semibold">
                        {t.jira_key}
                      </a>
                      <p className="text-xs text-[#6B7280] mt-0.5 max-w-[200px] truncate">{t.title}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={priorityColor[t.priority] ?? "text-[#6B7280]"}>{t.priority}</span>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="px-6 py-4 text-[#6B7280] font-medium">{daysOpen(t.created_at)}d</td>
                    <td className="px-6 py-4">
                      {isLoopClosed(t.status) ? (
                        <div className="flex flex-col gap-2">
                          <span className="text-[11px] bg-[#0F6E56]/10 text-[#0F6E56] border border-[#0F6E56]/20 font-bold px-3 py-0.5 rounded-full w-fit">Loop closed</span>
                          {slackSent === t.jira_id ? (
                            <span className="text-xs text-emerald-600 font-semibold">Sent to #customer-success ✓</span>
                          ) : (
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => sendToSlack(t)}
                                disabled={slackSending === t.jira_id}
                                className="text-xs bg-[#E8503A] hover:bg-[#d44432] disabled:opacity-50 text-white px-3 py-1 rounded-full font-semibold transition-colors"
                              >
                                {slackSending === t.jira_id ? "Sending…" : "Send to Slack"}
                              </button>
                              <button
                                onClick={() => copyNotification(t)}
                                className="text-xs text-[#6B7280] hover:text-[#1A1A1A] font-semibold transition-colors"
                              >
                                {copied === t.jira_id ? "Copied!" : "Copy message"}
                              </button>
                            </div>
                          )}
                          {slackError === t.jira_id && (
                            <span className="text-xs text-amber-600">Add Slack webhook in settings to enable</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-[#6B7280]">Awaiting resolution</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
