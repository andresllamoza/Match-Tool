"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BrandHeader } from "./BrandHeader";
import { CustomerHelpPanel } from "./CustomerHelpPanel";
import { JourneyFlow } from "./JourneyFlow";
import type { JourneyPhase } from "@/lib/types";

function CustomerJourney({ onPhaseChange }: { onPhaseChange: (phase: JourneyPhase) => void }) {
  const searchParams = useSearchParams();
  const initialEmployer = searchParams.get("employer") ?? "";

  return (
    <JourneyFlow mode="customer" initialEmployer={initialEmployer} onPhaseChange={onPhaseChange} />
  );
}

export function CustomerPageClient() {
  const [phase, setPhase] = useState<JourneyPhase>("find");

  return (
    <main className="mx-auto min-h-dvh max-w-journey bg-canvas px-4 py-6 sm:px-6 lg:max-w-desktop lg:px-8 lg:py-12">
      <BrandHeader mode="customer" />
      <p className="mb-6 hidden text-center text-bee-muted lg:mb-8 lg:block lg:text-lg">
        Roll your old 401(k) into a PensionBee IRA — one step at a time.
      </p>

      <div className="lg:grid lg:grid-cols-12 lg:gap-10">
        <div className="lg:col-span-7 xl:col-span-8">
          <Suspense
            fallback={
              <div className="flex min-h-[40dvh] items-center justify-center">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-bee-yellow/30 border-t-bee-yellow" />
              </div>
            }
          >
            <CustomerJourney onPhaseChange={setPhase} />
          </Suspense>
        </div>
        <div className="lg:col-span-5 xl:col-span-4">
          <CustomerHelpPanel phase={phase} />
        </div>
      </div>

      <p className="mt-8 text-center text-xs text-bee-muted lg:mt-12 lg:text-sm">
        Need help? A BeeKeeper is always available.
      </p>
    </main>
  );
}
