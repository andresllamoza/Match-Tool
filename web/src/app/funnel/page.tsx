"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getFunnel, type FunnelData } from "@/lib/api";
import { BrandHeader } from "@/components/BrandHeader";

export default function FunnelPage() {
  const [data, setData] = useState<FunnelData | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    getFunnel()
      .then((d) => {
        setData(d);
        setApiError(false);
      })
      .catch(() => {
        setData(null);
        setApiError(true);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="desktop-shell mx-auto min-h-dvh max-w-desktop px-4 py-6 lg:px-8 lg:py-10">
      <BrandHeader mode="agent" />
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4 lg:mb-8">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-bee-muted">Internal · Analytics</p>
          <h1 className="mt-1 text-2xl font-bold text-bee-charcoal lg:text-3xl">Funnel view</h1>
          <p className="mt-1 text-bee-muted lg:text-lg">
            Stall points by provider and channel — powered by journey event logs.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex min-h-[40dvh] items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
        </div>
      ) : apiError ? (
        <div className="rounded-card border border-bee-yellow/40 bg-bee-yellow-tint p-8 shadow-card">
          <p className="font-bold text-bee-charcoal">Analytics API unreachable</p>
          <p className="mt-2 text-sm leading-relaxed text-bee-ink">
            Funnel analytics need a live API. In demo mode, reload this page without{" "}
            <code className="rounded bg-white px-1.5 py-0.5 text-xs">API_URL</code> set, or connect Railway
            and set <code className="rounded bg-white px-1.5 py-0.5 text-xs">API_URL</code> on Vercel.
          </p>
        </div>
      ) : !data ? (
        <div className="rounded-card border border-bee-border bg-white p-8 text-center shadow-card">
          <p className="text-bee-muted">No journey data yet. Run a few rollovers first.</p>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3 lg:gap-8">
          <StatCard label="Journeys" value={String(data.total_journeys)} />
          <StatCard
            label="Completion rate"
            value={`${(data.completion_rate * 100).toFixed(0)}%`}
          />
          <StatCard
            label="Stall points"
            value={String(data.stall_points.reduce((a, s) => a + s.count, 0))}
          />

          <div className="rounded-card bg-white p-6 shadow-card lg:col-span-2 lg:p-8">
            <h2 className="mb-4 font-bold text-bee-charcoal">By state</h2>
            <BarChart data={data.by_state} />
          </div>

          <div className="rounded-card bg-white p-6 shadow-card lg:p-8">
            <h2 className="mb-4 font-bold text-bee-charcoal">By provider</h2>
            <BarChart data={data.by_provider} />
          </div>

          <div className="rounded-card bg-white p-6 shadow-card lg:col-span-2 lg:p-8">
            <h2 className="mb-4 font-bold text-bee-charcoal">Stall points</h2>
            {data.stall_points.length === 0 ? (
              <p className="text-bee-muted">No stalls recorded yet.</p>
            ) : (
              <table className="w-full text-left text-sm lg:text-base">
                <thead>
                  <tr className="border-b border-bee-border text-bee-muted">
                    <th className="pb-2 pr-4">State</th>
                    <th className="pb-2 pr-4">Provider</th>
                    <th className="pb-2 pr-4">Channel</th>
                    <th className="pb-2">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {data.stall_points.map((s, i) => (
                    <tr key={i} className="border-b border-bee-border/50">
                      <td className="py-2 pr-4 font-mono text-xs">{s.state}</td>
                      <td className="py-2 pr-4">{s.provider || "—"}</td>
                      <td className="py-2 pr-4">{s.channel || "—"}</td>
                      <td className="py-2 font-semibold">{s.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="rounded-card bg-white p-6 shadow-card lg:p-8">
            <h2 className="mb-4 font-bold text-bee-charcoal">By channel</h2>
            <BarChart data={data.by_channel} />
          </div>
        </div>
      )}

      <p className="mt-8 text-center">
        <Link href="/customer" className="font-semibold text-bee-charcoal hover:underline">
          ← Back to customer flow
        </Link>
      </p>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-card bg-white p-6 shadow-card lg:p-8">
      <p className="text-sm font-medium text-bee-muted lg:text-base">{label}</p>
      <p className="mt-1 text-3xl font-bold text-bee-charcoal lg:text-4xl">{value}</p>
    </div>
  );
}

function BarChart({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div className="space-y-3">
      {entries.map(([key, val]) => (
        <div key={key}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="font-medium">{key}</span>
            <span className="text-bee-muted">{val}</span>
          </div>
          <div className="h-2 rounded-pill bg-cream-dark">
            <div
              className="h-full rounded-pill bg-bee-yellow"
              style={{ width: `${(val / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
