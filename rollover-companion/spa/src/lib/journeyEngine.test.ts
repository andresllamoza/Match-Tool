import { describe, expect, it } from "vitest";
import { fboPayee, initialContext, reduceJourney } from "./journeyEngine";

describe("journeyEngine", () => {
  it("lookup amazon → fidelity", () => {
    let ctx = reduceJourney(initialContext(), { type: "lookup", employer: "Amazon" });
    expect(ctx.providerName).toBe("Fidelity");
    expect(ctx.screen).toBe("find_success");
  });

  it("walmart → not covered", () => {
    const ctx = reduceJourney(initialContext(), { type: "lookup", employer: "Walmart" });
    expect(ctx.screen).toBe("find_not_covered");
    expect(ctx.providerName).toBe("Merrill Lynch");
  });

  it("citi maps to alight not empower", () => {
    const ctx = reduceJourney(initialContext(), { type: "lookup", employer: "Citi" });
    expect(ctx.providerName).toBe("Alight Solutions");
    expect(ctx.matchedEmployer).toBe("Citigroup Inc.");
  });

  it("fbo always pensionbee", () => {
    let ctx = reduceJourney(initialContext(), { type: "lookup", employer: "Dollar Tree" });
    ctx = reduceJourney(ctx, { type: "continue" });
    ctx = reduceJourney(ctx, { type: "access", canLogin: true });
    ctx = reduceJourney(ctx, { type: "set_name", firstName: "Avery", lastName: "Quinn" });
    expect(fboPayee(ctx)).toBe("PensionBee FBO Avery Quinn");
  });

  it("stuck twice escalates", () => {
    let ctx = initialContext();
    ctx = { ...ctx, screen: "channel_step", phase: "rollover", providerId: "fidelity", channel: "online", stepIndex: 0 };
    ctx = reduceJourney(ctx, { type: "step_stuck" });
    expect(ctx.screen).toBe("stuck");
    ctx = { ...ctx, screen: "channel_step", stepIndex: 0 };
    ctx = reduceJourney(ctx, { type: "step_stuck" });
    expect(ctx.screen).toBe("escalated");
  });
});
