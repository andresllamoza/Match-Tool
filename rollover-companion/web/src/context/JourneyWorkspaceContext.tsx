"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { JourneyController } from "@/hooks/useJourneyController";

const JourneyWorkspaceContext = createContext<JourneyController | null>(null);

export function JourneyWorkspaceProvider({
  value,
  children,
}: {
  value: JourneyController;
  children: ReactNode;
}) {
  return (
    <JourneyWorkspaceContext.Provider value={value}>{children}</JourneyWorkspaceContext.Provider>
  );
}

export function useWorkspace(): JourneyController {
  const ctx = useContext(JourneyWorkspaceContext);
  if (!ctx) {
    throw new Error("useWorkspace must be used within JourneyWorkspaceProvider");
  }
  return ctx;
}
