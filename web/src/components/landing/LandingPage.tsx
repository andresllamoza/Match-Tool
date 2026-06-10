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

const TIMELINE = [
  { id: "find", label: "Find" },
  { id: "access", label: "Access" },
  { id: "rollover", label: "Roll over" },
  { id: "track", label: "Track" },
] as const;

const TRUST_CARDS = [
  {
    title: "Built-in Routing Safeguards",
    copy: "Zero guesswork. Your check is automatically coded to protect your tax status and enforce absolute FBO payee compliance.",
  },
  {
    title: "Verified Custodian Paths",
    copy: "Step-by-step navigation and exact spoken phrases tailored directly to major 401(k) providers.",
  },
  {
    title: "Save & Resume Anytime",
    copy: "Continuous session state resilience. Your progress saves with every action—pause or resume without data loss.",
  },
] as const;

function LandingTimeline() {
  return (
    <nav className="mb-10" aria-label="Rollover journey steps">
      <div className="flex gap-2">
        {TIMELINE.map((step, i) => {
          const active = i === 0;
          return (
            <div key={step.id} className="flex flex-1 flex-col">
              <div className="relative h-1 overflow-hidden rounded-full bg-[#EAE5DC]">
                {active && (
                  <motion.div
                    className="absolute inset-y-0 left-0 rounded-full bg-[#FFC72C]"
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ type: "spring", stiffness: 380, damping: 32, delay: 0.15 }}
                  />
                )}
              </div>
              <span
                className={`mt-2 text-[10px] font-bold uppercase tracking-[0.08em] ${
                  active ? "text-[#111111]" : "text-[#6B6560]"
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </nav>
  );
}

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

      <main className="relative mx-auto flex min-h-dvh w-full max-w-4xl flex-col justify-center px-6 py-16">
        <motion.div custom={0} variants={fadeUp} initial="hidden" animate="show">
          <LandingTimeline />
        </motion.div>

        <motion.div custom={1} variants={fadeUp} initial="hidden" animate="show">
          <span className="mb-3 block text-[11px] font-bold uppercase tracking-[0.2em] text-gray-400">
            Rollover Companion
          </span>

          <h1 className="mb-6 text-4xl font-extrabold leading-[1.1] tracking-[-0.03em] text-[#111111] sm:text-5xl">
            Move your old 401(k) to PensionBee — calmly, step by step.
          </h1>

          <p className="mb-8 max-w-xl text-lg leading-relaxed text-gray-600">
            Find your plan, recover missing access, and move your savings using verified routing
            rules and exact phone scripts. A dedicated BeeKeeper is always one tap away.
          </p>
        </motion.div>

        <motion.div
          custom={3}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mb-10 grid grid-cols-1 gap-4 sm:grid-cols-3"
        >
          {TRUST_CARDS.map((card) => (
            <article
              key={card.title}
              className="rounded-xl border border-[#EAE5DC] bg-white p-5 shadow-card"
            >
              <h2 className="text-sm font-bold leading-snug text-[#111111]">{card.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-[#555555]">{card.copy}</p>
            </article>
          ))}
        </motion.div>

        <motion.div
          custom={4}
          variants={fadeUp}
          initial="hidden"
          animate="show"
          className="mt-2 max-w-xl"
        >
          <Link
            href="/app"
            className="pb-interactive flex min-h-[3.5rem] w-full items-center justify-center rounded-card bg-[#111111] px-6 text-center text-base font-bold text-white shadow-card hover:bg-[#1E242B]"
          >
            Start my rollover
          </Link>
        </motion.div>
      </main>
    </div>
  );
}
