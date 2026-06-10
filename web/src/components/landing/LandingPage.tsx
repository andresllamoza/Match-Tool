"use client";

import Link from "next/link";
import { motion } from "framer-motion";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, type: "spring", stiffness: 380, damping: 32 },
  }),
};

export function LandingPage() {
  return (
    <div className="desktop-shell relative min-h-dvh overflow-hidden">
      <motion.div
        className="pointer-events-none absolute -left-24 top-20 h-64 w-64 rounded-full bg-bee-yellow/20 blur-3xl"
        animate={{ scale: [1, 1.08, 1], opacity: [0.5, 0.7, 0.5] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="pointer-events-none absolute -right-16 bottom-32 h-72 w-72 rounded-full bg-bee-yellow/10 blur-3xl"
        animate={{ scale: [1, 1.12, 1], opacity: [0.35, 0.55, 0.35] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      />

      <main className="relative mx-auto flex min-h-dvh max-w-lg flex-col justify-center px-6 py-16">
        <motion.p
          custom={0}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mb-3 text-sm font-bold uppercase tracking-[0.12em] text-bee-muted"
        >
          Rollover companion
        </motion.p>
        <motion.h1
          custom={1}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="text-4xl font-bold leading-[1.08] tracking-tight text-bee-charcoal sm:text-5xl"
        >
          Roll your old 401(k) into PensionBee — calmly, step by step.
        </motion.h1>
        <motion.p
          custom={2}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mt-5 text-lg leading-relaxed text-bee-ink/90"
        >
          Find your plan, recover access, and move your money with exact phrases and verified
          check routing. A real BeeKeeper is one tap away.
        </motion.p>

        <motion.div
          custom={3}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mt-10 flex flex-col gap-3"
        >
          <Link
            href="/app"
            className="pb-interactive flex min-h-[3.25rem] items-center justify-center rounded-card bg-bee-charcoal px-6 text-center text-base font-semibold text-white shadow-card hover:bg-bee-ink"
          >
            Start my rollover
          </Link>
          <p className="text-center text-xs text-bee-muted">
            Same engine as your advisor tools — FBO payee compliance built in.
          </p>
        </motion.div>

        <motion.ul
          custom={4}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mt-12 space-y-3 border-t border-bee-border pt-8 text-sm text-bee-ink"
        >
          {[
            "Find → Access → Roll over → Track",
            "Verified transfer paths for major providers",
            "Save & resume anytime",
          ].map((line) => (
            <li key={line} className="flex items-start gap-2">
              <span className="mt-0.5 text-bee-yellow">✓</span>
              <span>{line}</span>
            </li>
          ))}
        </motion.ul>
      </main>
    </div>
  );
}
