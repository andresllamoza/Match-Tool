import { createContext, useContext } from "react";
import { useJourney, type JourneyStore } from "../hooks/useJourney";

const JourneyContext = createContext<JourneyStore | null>(null);

export function JourneyProvider({ children }: { children: React.ReactNode }) {
  const store = useJourney();
  return <JourneyContext.Provider value={store}>{children}</JourneyContext.Provider>;
}

export function useJourneyContext() {
  const ctx = useContext(JourneyContext);
  if (!ctx) throw new Error("useJourneyContext must be used within JourneyProvider");
  return ctx;
}
