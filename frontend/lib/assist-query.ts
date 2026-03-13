import type { Level } from "@/lib/types/api";
import { type AssistToggles } from "@/lib/types/app";


type SearchParamsLike = {
  get: (key: string) => string | null;
};


function parseFlag(rawValue: string | null) {
  return rawValue === "1" || rawValue === "true" || rawValue === "on";
}


export function readLevelFromSearchParams(searchParams: SearchParamsLike): Level | null {
  const rawValue = searchParams.get("level");

  if (rawValue === "GT" || rawValue === "S" || rawValue === "MGT") {
    return rawValue;
  }

  return null;
}


export function readAssistTogglesFromSearchParams(searchParams: SearchParamsLike) {
  return {
    hasExplicitParams:
      searchParams.get("assist") !== null ||
      searchParams.get("translation") !== null ||
      searchParams.get("tts") !== null ||
      searchParams.get("explain") !== null,
    toggles: {
      useAssistApi: parseFlag(searchParams.get("assist")),
      useApiTranslation: parseFlag(searchParams.get("translation")),
      useApiTts: parseFlag(searchParams.get("tts")),
      useApiExplain: parseFlag(searchParams.get("explain")),
    } satisfies AssistToggles,
  };
}


export function buildAssistQueryString(toggles: AssistToggles, level?: Level | null) {
  const searchParams = new URLSearchParams();

  if (level) {
    searchParams.set("level", level);
  }

  searchParams.set("assist", toggles.useAssistApi ? "1" : "0");
  searchParams.set("translation", toggles.useApiTranslation ? "1" : "0");
  searchParams.set("tts", toggles.useApiTts ? "1" : "0");
  searchParams.set("explain", toggles.useApiExplain ? "1" : "0");

  return searchParams.toString();
}
