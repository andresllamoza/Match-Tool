"use client";

import { useState } from "react";
import { journeyAction } from "@/lib/api";
import type { AssistantResult } from "@/lib/types";
import { Button } from "./ui/Button";

interface AssistantDrawerProps {
  journeyId: string;
  open: boolean;
  onClose: () => void;
  onEscalate: () => void;
}

export function AssistantDrawer({
  journeyId,
  open,
  onClose,
  onEscalate,
}: AssistantDrawerProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AssistantResult | null>(null);

  if (!open) return null;

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await journeyAction(journeyId, { type: "ask", question });
      setResult(res.assistant || null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/30 p-4 lg:items-center">
      <div className="w-full max-w-lg rounded-card bg-white p-6 shadow-card-lg lg:p-8">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-bold text-bee-blue lg:text-xl">Ask a question</h3>
          <button
            onClick={onClose}
            className="text-bee-muted hover:text-bee-ink"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        <p className="mb-4 text-sm text-bee-muted lg:text-base">
          Scoped to your current step and our provider guides only.
        </p>
        <form onSubmit={handleAsk} className="space-y-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Where does the check get mailed?"
            className="w-full rounded-card border border-bee-border bg-cream px-4 py-3 text-base outline-none focus:border-bee-blue focus:ring-2 focus:ring-bee-blue/20 lg:py-4"
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Thinking…" : "Ask"}
          </Button>
        </form>
        {result && (
          <div
            className={`mt-4 rounded-card p-4 text-sm lg:text-base ${
              result.in_scope ? "bg-bee-blue-light text-bee-ink" : "bg-red-50 text-red-800"
            }`}
          >
            {result.answer}
          </div>
        )}
        <button
          onClick={onEscalate}
          className="mt-4 w-full text-center text-sm font-semibold text-bee-blue hover:underline lg:text-base"
        >
          Talk to a BeeKeeper instead →
        </button>
      </div>
    </div>
  );
}
