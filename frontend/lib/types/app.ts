import type { Level } from "@/lib/types/api";


export type AssistToggles = {
  useAssistApi: boolean;
  useApiTranslation: boolean;
  useApiTts: boolean;
  useApiExplain: boolean;
};

export type SessionDraft = {
  level: Level | null;
  toggles: AssistToggles;
};

export const defaultAssistToggles: AssistToggles = {
  useAssistApi: false,
  useApiTranslation: false,
  useApiTts: false,
  useApiExplain: false,
};
