"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getJourney, journeyAction, listProviders, startJourney } from "@/lib/api";
import { buildPathEntry, type PathHistoryEntry } from "@/lib/pathHistory";
import {
  clearJourneySession,
  isResumableSession,
  loadJourneySession,
  MAX_PATH_ENTRIES,
  resumeProviderLabel,
  saveJourneySession,
} from "@/lib/sessionPersistence";
import type { JourneyPhase, JourneyResponse } from "@/lib/types";

export interface ResumeOffer {
  providerName: string;
  stepNumber: number;
  journeyId: string;
}

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
  resumeOffer: ResumeOffer | null;
  resumeSession: () => Promise<void>;
  dismissResumeOffer: () => void;
  escalationConnecting: boolean;
  escalationActive: boolean;
  clearEscalationAlert: () => void;
  pathHistory: PathHistoryEntry[];
  validationShake: boolean;
  triggerValidationShake: () => void;
  escalateWithHandshake: (reason: string) => Promise<void>;
  stalledStep: number | null;
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
  const [resumeOffer, setResumeOffer] = useState<ResumeOffer | null>(null);
  const [escalationConnecting, setEscalationConnecting] = useState(false);
  const [escalationActive, setEscalationActive] = useState(false);
  const [pathHistory, setPathHistory] = useState<PathHistoryEntry[]>([]);
  const [validationShake, setValidationShake] = useState(false);
  const [stalledStep, setStalledStep] = useState<number | null>(null);
  const bootstrappedRef = useRef(false);
  const actInFlightRef = useRef(false);
  const escalationInFlightRef = useRef(false);

  const triggerValidationShake = useCallback(() => {
    setValidationShake(true);
    window.setTimeout(() => setValidationShake(false), 520);
  }, []);

  const clearEscalationAlert = useCallback(() => {
    setEscalationActive(false);
  }, []);

  const dismissResumeOffer = useCallback(() => {
    setResumeOffer(null);
    clearJourneySession();
  }, []);

  const applyResponse = useCallback(
    (res: JourneyResponse, action = "snapshot") => {
      setData(res);
      onPhaseChange?.(res.screen.phase);
      setPathHistory((prev) =>
        [...prev, buildPathEntry(res, action)].slice(-MAX_PATH_ENTRIES)
      );
      if (res.screen.state === "escalated") {
        setEscalationActive(true);
      }
    },
    [onPhaseChange]
  );

  useEffect(() => {
    if (!data || !isResumableSession(data)) {
      if (data && !isResumableSession(data)) clearJourneySession();
      return;
    }
    saveJourneySession({
      journeyId: data.context.journey_id,
      snapshot: data,
      employerInput,
      showProviderPicker,
      pathHistory,
    });
  }, [data, employerInput, showProviderPicker, pathHistory]);

  const act = useCallback(
    async (body: Record<string, unknown>) => {
      if (!data || actInFlightRef.current) return;
      actInFlightRef.current = true;
      setLoading(true);
      setError(null);
      try {
        const res = await journeyAction(data.context.journey_id, body, withAgentIntel);
        if (body.type === "step" && body.outcome === "stuck") {
          setStalledStep(data.step_index);
        }
        applyResponse(res, String(body.type || "action"));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong. A BeeKeeper can help.");
        triggerValidationShake();
      } finally {
        actInFlightRef.current = false;
        setLoading(false);
      }
    },
    [applyResponse, data, triggerValidationShake, withAgentIntel]
  );

  const escalateWithHandshake = useCallback(
    async (reason: string) => {
      if (!data || escalationInFlightRef.current) return;
      escalationInFlightRef.current = true;
      setStalledStep(data.step_index);
      setEscalationConnecting(true);
      setAssistantOpen(false);
      setError(null);
      try {
        const res = await journeyAction(
          data.context.journey_id,
          { type: "escalate", reason },
          withAgentIntel
        );
        applyResponse(res, "escalate");
        setEscalationActive(true);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Could not connect to a BeeKeeper. Please try again.");
        triggerValidationShake();
      } finally {
        escalationInFlightRef.current = false;
        setEscalationConnecting(false);
      }
    },
    [applyResponse, data, triggerValidationShake, withAgentIntel]
  );

  const restart = useCallback(async () => {
    clearJourneySession();
    setResumeOffer(null);
    setLoading(true);
    setError(null);
    setShowProviderPicker(false);
    setAssistantOpen(false);
    setEmployerInput("");
    setPathHistory([]);
    setEscalationActive(false);
    setEscalationConnecting(false);
    setStalledStep(null);
    try {
      const res = await startJourney(withAgentIntel);
      applyResponse(res, "restart");
    } catch {
      setError("Could not restart the journey. A BeeKeeper can help.");
      triggerValidationShake();
    } finally {
      setLoading(false);
    }
  }, [applyResponse, triggerValidationShake, withAgentIntel]);

  const resumeSession = useCallback(async () => {
    const saved = loadJourneySession();
    if (!saved) {
      setResumeOffer(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      let res: JourneyResponse;
      try {
        res = await getJourney(saved.journeyId, withAgentIntel);
      } catch {
        res = saved.snapshot;
      }
      setEmployerInput(saved.employerInput);
      setShowProviderPicker(saved.showProviderPicker);
      if (saved.pathHistory?.length) {
        setPathHistory(saved.pathHistory.slice(-MAX_PATH_ENTRIES));
      }
      applyResponse(res, "resume");
      setResumeOffer(null);
    } catch {
      setError("We couldn't restore your session. Starting fresh may be easiest.");
      clearJourneySession();
      setResumeOffer(null);
      triggerValidationShake();
    } finally {
      setLoading(false);
    }
  }, [applyResponse, triggerValidationShake, withAgentIntel]);

  useEffect(() => {
    if (!autoStart || bootstrappedRef.current) return;
    bootstrappedRef.current = true;

    let cancelled = false;
    const employerSeed = initialEmployer.trim();
    const providerSeed = initialProvider.trim();
    if (employerSeed) setEmployerInput(employerSeed);

    const saved = loadJourneySession();
    if (saved && isResumableSession(saved.snapshot) && !employerSeed && !providerSeed) {
      setResumeOffer({
        providerName: resumeProviderLabel(saved.snapshot),
        stepNumber: saved.snapshot.step_index + 1,
        journeyId: saved.journeyId,
      });
      setLoading(false);
      return;
    }

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

        applyResponse(res, "start");
        try {
          const prov = await listProviders();
          if (!cancelled) setProviders(prov.providers || []);
        } catch {
          if (!cancelled) setProviders([]);
        }
      } catch {
        if (!cancelled) {
          setError("Could not connect to the rollover engine. A BeeKeeper can help.");
          triggerValidationShake();
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [
    applyResponse,
    autoStart,
    initialEmployer,
    initialProvider,
    triggerValidationShake,
    withAgentIntel,
  ]);

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
    resumeOffer,
    resumeSession,
    dismissResumeOffer,
    escalationConnecting,
    escalationActive,
    clearEscalationAlert,
    pathHistory,
    validationShake,
    triggerValidationShake,
    escalateWithHandshake,
    stalledStep,
  };
}
