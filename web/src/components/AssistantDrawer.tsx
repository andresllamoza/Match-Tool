"use client";

import { useEffect, useState } from "react";
import { journeyAction } from "@/lib/api";
import { getAssistantSuggestions } from "@/lib/assistantSuggestions";
import type { AssistantResult, JourneyScreen } from "@/lib/types";
import { Button } from "./ui/Button";

interface AssistantDrawerProps {
  journeyId: string;
  screen: JourneyScreen;
  open: boolean;
  onClose: () => void;
  onEscalate: () => void;
}

export function AssistantDrawer({
  journeyId,
  screen,
  open,
  onClose,
  onEscalate,
}: AssistantDrawerProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AssistantResult | null>(null);
  const suggestions = getAssistantSuggestions(screen);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  async function ask(q: string) {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuestion(trimmed);
    setLoading(true);
    setResult(null);
    try {
      const res = await journeyAction(journeyId, { type: "ask", question: trimmed });
      setResult(res.assistant || null);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await ask(question);
  }

  return (
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label="Step assistant">
      <button
        type="button"
        className="absolute inset-0 animate-fade-in bg-bee-charcoal/40 backdrop-blur-[2px]"
        onClick={onClose}
        aria-label="Close assistant"
      />

      <div
        className="pb-sheet absolute inset-x-0 bottom-0 flex max-h-[88dvh] flex-col rounded-t-[20px] border-t border-bee-border shadow-sheet animate-sheet-up lg:inset-y-0 lg:left-auto lg:right-0 lg:max-h-none lg:w-full lg:max-w-md lg:rounded-none lg:rounded-l-[20px] lg:border-l lg:border-t-0 lg:animate-sheet-right"
      >
        <div className="flex shrink-0 items-center justify-center pt-3 lg:hidden">
          <div className="h-1 w-10 rounded-pill bg-bee-border" aria-hidden />
        </div>

        <div className="flex shrink-0 items-start justify-between gap-4 border-b border-bee-border/80 px-5 pb-4 pt-3 lg:px-6 lg:pt-6">
          <div>
            <h3 className="text-lg font-bold text-bee-charcoal lg:text-xl">Ask about this step</h3>
            <p className="mt-1 text-sm leading-relaxed text-bee-muted">
              Answers come from your provider guide and PensionBee rollover rules only.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-bee-muted transition-colors hover:bg-cream-dark hover:text-bee-charcoal"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 lg:px-6">
          <p className="mb-3 text-xs font-bold uppercase tracking-wide text-bee-muted">
            Common questions
          </p>
          <div className="space-y-2">
            {suggestions.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => ask(s)}
                disabled={loading}
                className="flex min-h-[52px] w-full items-center rounded-card border-2 border-bee-border bg-white px-4 py-3 text-left text-sm font-semibold leading-snug text-bee-charcoal transition-all hover:border-bee-charcoal/30 hover:bg-bee-yellow-soft/40 active:scale-[0.98] disabled:opacity-50 lg:text-base"
              >
                {s}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-3">
            <label className="block text-xs font-bold uppercase tracking-wide text-bee-muted">
              Or type your own
            </label>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Where does the check get mailed?"
              className="w-full rounded-card border-2 border-bee-border bg-white px-4 py-3.5 text-base text-bee-charcoal outline-none transition-colors placeholder:text-bee-muted/70 focus:border-bee-yellow focus:ring-2 focus:ring-bee-yellow/30"
            />
            <Button type="submit" disabled={loading || !question.trim()}>
              {loading ? "Thinking…" : "Ask"}
            </Button>
          </form>

          {result && (
            <div
              className={`mt-4 rounded-card p-4 text-sm leading-relaxed lg:text-base ${
                result.in_scope
                  ? "border border-bee-border bg-white text-bee-ink"
                  : "border border-red-200 bg-red-50 text-red-800"
              }`}
            >
              {result.answer}
            </div>
          )}
        </div>

        <div className="shrink-0 border-t border-bee-border/80 bg-cream-dark/30 px-5 py-4 lg:px-6">
          <Button type="button" variant="beekeeper" onClick={onEscalate}>
            Skip this step and talk directly to a human BeeKeeper
          </Button>
        </div>
      </div>
    </div>
  );
}
