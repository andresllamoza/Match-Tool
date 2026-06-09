import type { JourneyScreen } from "./types";

export function getAssistantSuggestions(screen: JourneyScreen): string[] {
  const provider = screen.provider || "your old provider";
  const state = screen.state;
  const channel = screen.channel;

  if (state === "provider_unknown") {
    return [
      "What if I don't have my old statement?",
      "How do you find my 401(k) provider?",
      "Can I roll over if I still work there?",
    ];
  }

  if (state === "provider_identified" || state === "provider_not_covered") {
    return [
      "What if I can't log in to my old account?",
      `Is ${provider} definitely my recordkeeper?`,
      "What documents should I have ready?",
    ];
  }

  if (state === "access_blocked") {
    return [
      "How long does password recovery usually take?",
      "What if I never got my login details?",
      "Can PensionBee contact my old provider for me?",
    ];
  }

  if (channel === "phone" || state === "phone_in_progress") {
    return [
      "Where do I send the rollover check?",
      "What if the phone menu options sound different?",
      "What should I say if they ask for my SSN?",
    ];
  }

  if (channel === "online" || state === "online_in_progress") {
    return [
      "What if I don't see a rollover option?",
      "Where does the check get mailed?",
      "What destination should I pick in the dropdown?",
    ];
  }

  if (channel === "forms" || state === "forms_in_progress") {
    return [
      "Where can I download the distribution form?",
      "What address goes in the receiving provider field?",
      "Do I mail the form or upload it online?",
    ];
  }

  if (state === "initiated" || state === "in_flight") {
    return [
      "How long does a rollover usually take?",
      "What if nothing arrived by the expected date?",
      "Who do I call if the check is lost?",
    ];
  }

  if (state === "stuck") {
    return [
      "Can a BeeKeeper finish this step for me?",
      "Will I have to start the rollover over?",
      "What information does support need from me?",
    ];
  }

  return [
    "What happens after I complete this step?",
    "Is my money safe during a rollover?",
    "Can I talk to someone about my specific plan?",
  ];
}
