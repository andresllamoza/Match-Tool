"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BrandHeader } from "./BrandHeader";
import { CustomerHelpPanel } from "./CustomerHelpPanel";
import { JourneyFlow } from "./JourneyFlow";
import { useJourneyController } from "@/hooks/useJourneyController";
import type { JourneyPhase } from "@/lib/types";

function CustomerContent() {
  const searchParams = useSearchParams();
  const [phase, setPhase] = useState<JourneyPhase>("find");
  const initialEmployer = searchParams.get("employer") ?? "";
  const initialProvider = searchParams.get("provider") ?? "";

  const controller = useJourneyController({
    initialEmployer,
    initialProvider,
    onPhaseChange: setPhase,
  });

  return (
    <>
      <BrandHeader
        mode="customer"
        actions={
          <button
            type="button"
            onClick={() => controller.restart()}
            disabled={controller.loading}
            title="Restart journey"
            className="flex h-11 w-11 items-center justify-center rounded-xl border border-bee-border bg-white text-lg text-bee-charcoal transition hover:border-bee-charcoal disabled:opacity-50"
          >
            ↺
          </button>
        }
      />
      <p className="mb-6 hidden text-center text-bee-muted lg:mb-8 lg:block lg:text-lg">
        Roll your old 401(k) into a PensionBee IRA — one step at a time.
      </p>

      <div className="lg:grid lg:grid-cols-12 lg:gap-10">
        <div className="lg:col-span-7 xl:col-span-8">
          <JourneyFlow mode="customer" controller={controller} onPhaseChange={setPhase} />
        </div>
        <div className="hidden lg:col-span-5 lg:block xl:col-span-4">
          <CustomerHelpPanel phase={phase} />
        </div>
      </div>

      <p className="mt-8 text-center text-xs text-bee-muted lg:mt-12 lg:text-sm">
        Need help? A BeeKeeper is always available.
      </p>
    </>
  );
}

export function CustomerPageClient() {
  return (
    <main className="mx-auto min-h-dvh max-w-journey bg-canvas px-4 py-6 sm:px-6 lg:max-w-desktop lg:px-8 lg:py-12">
      <Suspense
        fallback={
          <div className="flex min-h-[50dvh] items-center justify-center">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
          </div>
        }
      >
        <CustomerContent />
      </Suspense>
    </main>
  );
}
