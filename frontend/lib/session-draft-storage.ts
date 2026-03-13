import { defaultAssistToggles, type AssistToggles, type SessionDraft } from "@/lib/types/app";


const SESSION_DRAFT_STORAGE_KEY = "reading-ella-session-draft";
const SESSION_DRAFT_CHANGED_EVENT = "reading-ella-session-draft-changed";
const VALID_LEVELS = new Set(["GT", "S", "MGT"]);
const DEFAULT_SESSION_DRAFT: SessionDraft = {
  level: null,
  toggles: { ...defaultAssistToggles },
};

let cachedRawValue: string | null | undefined;
let cachedSnapshot: SessionDraft = DEFAULT_SESSION_DRAFT;


function getDefaultDraft(): SessionDraft {
  return DEFAULT_SESSION_DRAFT;
}


function toBoolean(value: unknown) {
  return value === true;
}


function normalizeSessionDraft(parsed: Partial<SessionDraft> | null): SessionDraft {
  try {
    if (!parsed || typeof parsed !== "object") {
      return getDefaultDraft();
    }

    const level =
      typeof parsed.level === "string" && VALID_LEVELS.has(parsed.level) ? parsed.level : null;
    const toggles: Partial<AssistToggles> =
      parsed.toggles && typeof parsed.toggles === "object" ? parsed.toggles : {};

    return {
      level,
      toggles: {
        useAssistApi: toBoolean(toggles.useAssistApi),
        useApiTranslation: toBoolean(toggles.useApiTranslation),
        useApiTts: toBoolean(toggles.useApiTts),
        useApiExplain: toBoolean(toggles.useApiExplain),
      },
    };
  } catch {
    return getDefaultDraft();
  }
}


function readSessionDraftFromStorage(rawValue: string | null): SessionDraft {
  if (!rawValue) {
    return getDefaultDraft();
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<SessionDraft> | null;
    return normalizeSessionDraft(parsed);
  } catch {
    return getDefaultDraft();
  }
}


export function getServerSessionDraftSnapshot(): SessionDraft {
  return DEFAULT_SESSION_DRAFT;
}


export function getSessionDraftSnapshot(): SessionDraft {
  if (typeof window === "undefined") {
    return getServerSessionDraftSnapshot();
  }

  const rawValue = window.localStorage.getItem(SESSION_DRAFT_STORAGE_KEY);
  if (rawValue === cachedRawValue) {
    return cachedSnapshot;
  }

  cachedRawValue = rawValue;
  cachedSnapshot = readSessionDraftFromStorage(rawValue);
  return cachedSnapshot;
}


export function loadSessionDraft(): SessionDraft {
  return getSessionDraftSnapshot();
}


export function saveSessionDraft(draft: SessionDraft) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    const normalizedDraft = normalizeSessionDraft(draft);
    const rawValue = JSON.stringify(normalizedDraft);

    window.localStorage.setItem(SESSION_DRAFT_STORAGE_KEY, rawValue);
    cachedRawValue = rawValue;
    cachedSnapshot = normalizedDraft;
    window.dispatchEvent(new Event(SESSION_DRAFT_CHANGED_EVENT));
  } catch {
    // Ignore storage errors in the scaffold stage.
  }
}


export function subscribeSessionDraft(onStoreChange: () => void) {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  function handleStorage(event: StorageEvent) {
    if (event.key === null || event.key === SESSION_DRAFT_STORAGE_KEY) {
      onStoreChange();
    }
  }

  window.addEventListener("storage", handleStorage);
  window.addEventListener(SESSION_DRAFT_CHANGED_EVENT, onStoreChange);

  return () => {
    window.removeEventListener("storage", handleStorage);
    window.removeEventListener(SESSION_DRAFT_CHANGED_EVENT, onStoreChange);
  };
}
