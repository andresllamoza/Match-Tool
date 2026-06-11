"use client";

import { Suspense, useCallback, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { JourneyFlow } from "./JourneyFlow";
import { AppShell } from "./shell/AppShell";
import { Button } from "./ui/Button";
import { useJourneyController } from "@/hooks/useJourneyController";
import type { JourneyPhase, JourneyResponse } from "@/lib/types";
import { resolveFooterActions } from "@/lib/footerActions";

function canGoBack(data: JourneyResponse | null, employerDraft: string): boolean {
  if (!data?.context.history_stack?.length) return false;
  if (data.screen.state === "complete") return false;
  if (data.screen.state === "provider_unknown" && !data.context.employer_query && !employerDraft) {
    return false;
  }
  return true;
}

function AppContent() {
  const searchParams = useSearchParams();
  const [phase, setPhase] = useState<JourneyPhase>("find");
  const initialEmployer = searchParams.get("employer") ?? "";
  const initialProvider = searchParams.get("provider") ?? "";

  const controller = useJourneyController({
    initialEmployer,
    initialProvider,
    onPhaseChange: setPhase,
  });

  const {
    data,
    act,
    loading,
    employerInput,
    restart,
    escalateWithHandshake,
    setAssistantOpen,
  } = controller;
  const [savedToast, setSavedToast] = useState(false);

  const showBack = useMemo(
    () => canGoBack(data, employerInput),
    [data, employerInput]
  );

  const handleBack = useCallback(() => {
    void act({ type: "go_back" });
  }, [act]);

  const handleSaveExit = useCallback(() => {
    if (typeof window !== "undefined") {
      window.sessionStorage.setItem("pb_saved_exit", String(Date.now()));
    }
    setSavedToast(true);
    window.setTimeout(() => setSavedToast(false), 3200);
  }, []);

  const footerSpec = data ? resolveFooterActions(data, controller.showProviderPicker) : null;

  const runFooterAction = (action: Record<string, unknown>) => {
    if (action.type === "restart") {
      void restart();
      return;
    }
    void act(action);
  };

  const footer = (
    <div className="space-y-2">
      {footerSpec?.secondaries.map((sec) => (
        <Button
          key={sec.key}
          variant="secondary"
          onClick={() => runFooterAction(sec.action)}
          disabled={loading}
          className="w-full"
        >
          {sec.label}
        </Button>
      ))}
      {footerSpec?.primary && (
        <Button
          onClick={() => runFooterAction(footerSpec.primary!.action)}
          disabled={loading}
          className="w-full"
        >
          {footerSpec.primary.label}
        </Button>
      )}
      <p className="pt-1 text-center text-xs text-bee-muted">Talk to your BeeKeeper</p>
      <button
        type="button"
        onClick={() => void escalateWithHandshake(`voluntary:${data?.screen.state ?? "find"}`)}
        disabled={loading}
        className="pb-interactive w-full py-2 text-center text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
      >
        Get a person to help
      </button>
    </div>
  );

  return (
    <>
      {savedToast && (
        <div
          className="fixed inset-x-0 top-4 z-[70] flex justify-center px-4"
          role="status"
          aria-live="polite"
        >
          <div className="animate-toast-up rounded-pill border border-bee-border bg-white px-5 py-3 text-sm font-semibold text-bee-charcoal shadow-card-lg">
            Progress saved — resume anytime from this device.
          </div>
        </div>
      )}
      <AppShell
        phase={phase}
        showBack={showBack}
        onBack={handleBack}
        onSaveExit={handleSaveExit}
        onOpenChat={() => setAssistantOpen(true)}
        showChatBubble={data != null && data.screen.state !== "complete"}
        footer={data ? footer : undefined}
        hideRail={data == null || data.screen.state === "complete"}
      >
        <JourneyFlow
          mode="customer"
          theme="minimal"
          controller={controller}
          onPhaseChange={setPhase}
          externalShell
        />
      </AppShell>
    </>
  );
}

export function AppPageClient() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-dvh items-center justify-center bg-canvas">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
        </div>
      }
    >
      <AppContent />
    </Suspense>
  );
}
