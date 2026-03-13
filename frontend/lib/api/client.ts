import { appConfig } from "@/lib/config";
import type {
  ApiErrorResponse,
  AttemptResultResponse,
  ExplanationRequest,
  ExplanationResponse,
  Level,
  PackLoadResponse,
  ReviewListResponse,
  SubmitRequest,
  SubmitResponse,
  TranslationRequest,
  TranslationResponse,
  TtsRequest,
  TtsResponse,
} from "@/lib/types/api";


export class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}


function buildUrl(path: string, searchParams?: Record<string, string | undefined>) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${appConfig.apiBaseUrl}${normalizedPath}`);

  if (searchParams) {
    for (const [key, value] of Object.entries(searchParams)) {
      if (value) {
        url.searchParams.set(key, value);
      }
    }
  }

  return url;
}


async function parseErrorMessage(response: Response) {
  try {
    const payload = (await response.json()) as ApiErrorResponse;
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
  } catch {
    return `요청에 실패했습니다. (${response.status})`;
  }

  return `요청에 실패했습니다. (${response.status})`;
}


async function apiRequest<T>(path: string, init?: RequestInit, searchParams?: Record<string, string | undefined>) {
  const response = await fetch(buildUrl(path, searchParams), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new ApiClientError(await parseErrorMessage(response), response.status);
  }

  return (await response.json()) as T;
}


export function getRandomPack(level: Level, lang = "ko") {
  return apiRequest<PackLoadResponse>("/packs", undefined, { level, lang });
}


export function getPackById(packId: string, lang = "ko") {
  return apiRequest<PackLoadResponse>(`/packs/${packId}`, undefined, { lang });
}


export function submitAnswers(payload: SubmitRequest) {
  return apiRequest<SubmitResponse>("/submissions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function getAttemptResult(attemptId: string) {
  return apiRequest<AttemptResultResponse>(`/results/${attemptId}`);
}


export function getReviewItems(limit = 50) {
  return apiRequest<ReviewListResponse>("/review-items", undefined, { limit: String(limit) });
}


export function requestTranslation(payload: TranslationRequest) {
  return apiRequest<TranslationResponse>("/assist/translation", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function requestExplanation(payload: ExplanationRequest) {
  return apiRequest<ExplanationResponse>("/assist/explanation", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


export function requestTts(payload: TtsRequest) {
  return apiRequest<TtsResponse>("/assist/tts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
