import { useCallback, useEffect, useMemo, useState } from "react";
import { initialContext, reduceJourney, STORAGE_KEY } from "../lib/journeyEngine";
import type { JourneyAction, JourneyContext, PersistedJourney } from "../types/journey";

function load(): JourneyContext | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PersistedJourney;
    if (parsed.version !== 1) return null;
    if (parsed.ctx.screen === "complete" || parsed.ctx.screen === "find") return null;
    return { ...parsed.ctx, welcomeBack: true };
  } catch {
    return null;
  }
}

function save(ctx: JourneyContext) {
  const payload: PersistedJourney = {
    version: 1,
    savedAt: new Date().toISOString(),
    ctx: { ...ctx, welcomeBack: false },
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
}

function clear() {
  localStorage.removeItem(STORAGE_KEY);
}

export function useJourney() {
  const [ctx, setCtx] = useState<JourneyContext>(() => {
    const restored = load();
    return restored ?? initialContext();
  });

  useEffect(() => {
    if (ctx.screen !== "find" || ctx.employerQuery) {
      save(ctx);
    }
  }, [ctx]);

  const dispatch = useCallback((action: JourneyAction) => {
    setCtx((prev) => {
      const next = reduceJourney(prev, action);
      if (action.type === "restart") {
        clear();
        return next;
      }
      return next;
    });
  }, []);

  const restart = useCallback(() => dispatch({ type: "restart" }), [dispatch]);

  return useMemo(
    () => ({
      ctx,
      dispatch,
      restart,
      dismissWelcome: () => dispatch({ type: "dismiss_welcome" }),
    }),
    [ctx, dispatch, restart]
  );
}

export type JourneyStore = ReturnType<typeof useJourney>;
