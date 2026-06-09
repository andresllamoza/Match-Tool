"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getFunnel, type FunnelData } from "@/lib/api";
import { BrandHeader } from "@/components/BrandHeader";

export default function FunnelPage() {
  const [data, setData] = useState<FunnelData | null>(null);

  useEffect(() => {
    getFunnel().then(setData).catch(() => setData(null));
  }, []);

  return (
    <main className="mx-auto min-h-dvh max-w-desktop px-4 py-6 lg:px-8 lg:py-10">
      <BrandHeader mode="customer" />
      <h1 className="mb-2 text-2xl font-bold text-bee-charcoal lg:text-3xl">Funnel view</h1>
      <p className="mb-8 text-bee-muted lg:text-lg">
        Stall points by provider and channel — powered by JourneyEvent JSONL.
      </p>

      {!data ? (
        <p className="text-bee-muted">No journey data yet. Run a few rollovers first.</p>
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
        <Link href="/" className="font-semibold text-bee-charcoal hover:underline">
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
