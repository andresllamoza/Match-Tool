"use client";

import { useCallback, useEffect, useState } from "react";
import { journeyAction, startJourney } from "@/lib/api";
import type { JourneyPhase, JourneyResponse } from "@/lib/types";

export interface JourneyController {
  data: JourneyResponse | null;
  loading: boolean;
  error: string | null;
  employerInput: string;
  setEmployerInput: (value: string) => void;
  showProviderPicker: boolean;
  setShowProviderPicker: (value: boolean) => void;
  providers: string[];
  assistantOpen: boolean;
  setAssistantOpen: (value: boolean) => void;
  act: (body: Record<string, unknown>) => Promise<void>;
  restart: () => Promise<void>;
  setError: (message: string | null) => void;
}

interface UseJourneyControllerOptions {
  withAgentIntel?: boolean;
  initialEmployer?: string;
  initialProvider?: string;
  onPhaseChange?: (phase: JourneyPhase) => void;
  autoStart?: boolean;
}

export function useJourneyController({
  withAgentIntel = false,
  initialEmployer = "",
  initialProvider = "",
  onPhaseChange,
  autoStart = true,
}: UseJourneyControllerOptions = {}): JourneyController {
  const [data, setData] = useState<JourneyResponse | null>(null);
  const [loading, setLoading] = useState(autoStart);
  const [error, setError] = useState<string | null>(null);
  const [employerInput, setEmployerInput] = useState("");
  const [showProviderPicker, setShowProviderPicker] = useState(false);
  const [providers, setProviders] = useState<string[]>([]);
  const [assistantOpen, setAssistantOpen] = useState(false);

  const act = useCallback(
    async (body: Record<string, unknown>) => {
      if (!data) return;
      setLoading(true);
      setError(null);
      try {
        const res = await journeyAction(data.context.journey_id, body, withAgentIntel);
        setData(res);
        onPhaseChange?.(res.screen.phase);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong. A BeeKeeper can help.");
      } finally {
        setLoading(false);
      }
    },
    [data, onPhaseChange, withAgentIntel]
  );

  const restart = useCallback(async () => {
    setLoading(true);
    setError(null);
    setShowProviderPicker(false);
    setAssistantOpen(false);
    setEmployerInput("");
    try {
      const res = await startJourney(withAgentIntel);
      setData(res);
      onPhaseChange?.(res.screen.phase);
    } catch {
      setError("Could not restart the journey. A BeeKeeper can help.");
    } finally {
      setLoading(false);
    }
  }, [onPhaseChange, withAgentIntel]);

  useEffect(() => {
    if (!autoStart) return;

    let cancelled = false;
    const employerSeed = initialEmployer.trim();
    const providerSeed = initialProvider.trim();
    if (employerSeed) setEmployerInput(employerSeed);

    (async () => {
      try {
        let res = await startJourney(withAgentIntel);
        if (cancelled) return;

        if (providerSeed && res.screen.state === "provider_unknown") {
          res = await journeyAction(
            res.context.journey_id,
            { type: "provider_direct", provider: providerSeed },
            withAgentIntel
          );
          if (cancelled) return;
        } else if (employerSeed && res.screen.state === "provider_unknown") {
          res = await journeyAction(
            res.context.journey_id,
            { type: "lookup", employer: employerSeed },
            withAgentIntel
          );
          if (cancelled) return;
        }

        setData(res);
        onPhaseChange?.(res.screen.phase);
        const prov = await fetch("/api/providers").then((r) => r.json());
        if (!cancelled) setProviders(prov.providers || []);
      } catch {
        if (!cancelled) {
          setError("Could not connect to the rollover engine. A BeeKeeper can help.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [autoStart, initialEmployer, initialProvider, onPhaseChange, withAgentIntel]);

  return {
    data,
    loading,
    error,
    employerInput,
    setEmployerInput,
    showProviderPicker,
    setShowProviderPicker,
    providers,
    assistantOpen,
    setAssistantOpen,
    act,
    restart,
    setError,
  };
}
