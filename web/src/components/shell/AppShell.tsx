"use client";

import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { JourneyPhase } from "@/lib/types";
import { FloatingChatBubble } from "./FloatingChatBubble";
import { MomentumRail } from "./MomentumRail";
import { PensionBeeSidebar } from "./PensionBeeSidebar";

interface AppShellProps {
  phase: JourneyPhase;
  showBack: boolean;
  onBack: () => void;
  onSaveExit: () => void;
  onOpenChat?: () => void;
  children: ReactNode;
  footer?: ReactNode;
  hideRail?: boolean;
  showChatBubble?: boolean;
}

export function AppShell({
  phase,
  showBack,
  onBack,
  onSaveExit,
  onOpenChat,
  children,
  footer,
  hideRail = false,
  showChatBubble = false,
}: AppShellProps) {
  const reduceMotion = useReducedMotion();

  return (
    <div className="desktop-shell relative mx-auto min-h-dvh max-w-desktop px-4 pb-36 pt-4 sm:px-6 lg:px-8">
      <div className="flex gap-8">
        <PensionBeeSidebar />

        <div className="mx-auto flex min-h-dvh w-full max-w-journey flex-1 flex-col">
          <header className="mb-4 grid grid-cols-[1fr_auto_1fr] items-center gap-2">
            <div className="justify-self-start">
              {showBack ? (
                <button
                  type="button"
                  onClick={onBack}
                  className="pb-interactive min-h-[44px] px-2 text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
                >
                  ← Back
                </button>
              ) : (
                <span className="inline-block w-12" aria-hidden />
              )}
            </div>
            <p className="text-center text-base font-extrabold tracking-tight text-bee-charcoal lg:hidden">
              PensionBee
            </p>
            <div className="justify-self-end">
              <button
                type="button"
                onClick={onSaveExit}
                className="pb-interactive min-h-[44px] px-2 text-sm font-semibold text-bee-muted hover:text-bee-charcoal"
              >
                Save &amp; exit
              </button>
            </div>
          </header>

          {!hideRail && <MomentumRail phase={phase} />}

          <motion.div
            key={phase}
            initial={reduceMotion ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={reduceMotion ? { duration: 0 } : { type: "spring", stiffness: 420, damping: 36 }}
            className="flex-1"
          >
            {children}
          </motion.div>
        </div>
      </div>

      {showChatBubble && onOpenChat && <FloatingChatBubble onClick={onOpenChat} />}

      {footer && (
        <div className="fixed inset-x-0 bottom-0 z-50 border-t border-bee-border bg-gradient-to-t from-canvas via-canvas to-canvas/80 px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-3 sm:mx-auto sm:max-w-journey lg:ml-[calc(14rem+2rem)] lg:max-w-[calc(28rem+14rem+2rem)]">
          {footer}
        </div>
      )}
    </div>
  );
}
